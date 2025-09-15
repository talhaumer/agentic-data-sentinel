"""LLM service for generating explanations and recommendations."""

import json
from typing import Dict, Any, Optional

import structlog
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage

from app.config import get_settings
from app.models import Anomaly
from app.schemas import LLMExplanationResponse

logger = structlog.get_logger(__name__)


class LLMService:
    """Service for LLM-powered explanations and recommendations."""

    def __init__(self):
        self.settings = get_settings()

        # Initialize LLM based on provider
        if self.settings.llm_provider.lower() == "groq":
            self.llm = ChatGroq(
                model_name=self.settings.llm_model,
                groq_api_key=self.settings.llm_api_key,
                temperature=0.1,
                max_tokens=1000,
            )
        else:  # Default to OpenAI
            self.llm = ChatOpenAI(
                model_name=self.settings.llm_model,
                openai_api_key=self.settings.llm_api_key,
                temperature=0.1,
                max_tokens=1000,
            )

    async def explain_anomaly(
        self, anomaly: Anomaly, context: Optional[Dict[str, Any]] = None
    ) -> LLMExplanationResponse:
        """Generate LLM explanation for an anomaly."""
        try:
            logger.info("Generating LLM explanation", anomaly_id=anomaly.id)

            # Build context for the LLM
            anomaly_context = {
                "anomaly_id": anomaly.id,
                "dataset_name": anomaly.table_name,
                "column_name": anomaly.column_name,
                "issue_type": anomaly.issue_type,
                "severity": anomaly.severity,
                "description": anomaly.description,
                "detected_at": anomaly.detected_at.isoformat(),
                "extra_data": anomaly.extra or {},
            }

            if context:
                anomaly_context.update(context)

            # Create prompt
            prompt = self._build_explanation_prompt(anomaly_context)

            # Get LLM response
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.agenerate([messages])
            response_text = response.generations[0][0].text

            # Parse response
            explanation = self._parse_llm_response(response_text)

            logger.info("LLM explanation generated", anomaly_id=anomaly.id)
            return explanation

        except Exception as e:
            logger.error(
                "Failed to generate LLM explanation",
                anomaly_id=anomaly.id,
                error=str(e),
            )
            # Return fallback explanation
            return LLMExplanationResponse(
                explanation=f"Unable to generate explanation for {anomaly.issue_type} anomaly in {anomaly.column_name}",
                confidence=0.0,
                suggested_sql=None,
                action_type="no_action",
            )

    def _build_explanation_prompt(self, context: Dict[str, Any]) -> str:
        """Build the prompt for LLM explanation."""
        return f"""
You are a Data Steward assistant. Given the following anomaly metadata and context, explain the most likely root cause and propose remediation steps.

Anomaly Details:
- ID: {context['anomaly_id']}
- Dataset: {context['dataset_name']}
- Column: {context['column_name']}
- Issue Type: {context['issue_type']}
- Severity: {context['severity']}/5
- Description: {context['description']}
- Detected At: {context['detected_at']}
- Extra Data: {json.dumps(context['extra_data'], indent=2)}

Please provide a JSON response with the following structure:
{{
    "explanation": "Human-readable explanation of the likely root cause",
    "confidence": 0.85,
    "suggested_sql": "SELECT or UPDATE statement to investigate or fix the issue (if applicable)",
    "action_type": "auto_fix|notify_owner|create_issue|no_action"
}}

Guidelines:
- Be specific about the likely root cause
- Provide actionable remediation steps
- Only suggest SQL that is safe and non-destructive
- Choose appropriate action type based on severity and confidence
- If suggesting SQL, make it a SELECT statement for investigation first
"""

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM."""
        return """
You are an expert Data Steward with deep knowledge of data quality issues, ETL processes, and data engineering best practices.

Your role is to:
1. Analyze data quality anomalies and identify root causes
2. Provide clear, actionable explanations
3. Suggest safe remediation steps
4. Recommend appropriate actions based on severity and context

Key principles:
- Always prioritize data safety
- Suggest investigation before fixes
- Consider upstream dependencies
- Provide specific, actionable recommendations
- Use appropriate confidence levels
- Choose safe action types (investigate before fixing)
"""

    def _parse_llm_response(self, response_text: str) -> LLMExplanationResponse:
        """Parse the LLM response into structured format."""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)

                return LLMExplanationResponse(
                    explanation=data.get("explanation", "No explanation provided"),
                    confidence=float(data.get("confidence", 0.5)),
                    suggested_sql=data.get("suggested_sql"),
                    action_type=data.get("action_type", "no_action"),
                )
            else:
                # Fallback if no JSON found
                return LLMExplanationResponse(
                    explanation=response_text.strip(),
                    confidence=0.5,
                    suggested_sql=None,
                    action_type="no_action",
                )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(
                "Failed to parse LLM response", error=str(e), response=response_text
            )
            return LLMExplanationResponse(
                explanation=response_text.strip(),
                confidence=0.3,
                suggested_sql=None,
                action_type="no_action",
            )

    async def generate_recommendations(
        self, dataset_id: int, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate general recommendations for a dataset."""
        try:
            prompt = f"""
Based on the following dataset context, provide recommendations for improving data quality:

Dataset Context:
{json.dumps(context, indent=2)}

Please provide recommendations in JSON format:
{{
    "data_quality_improvements": ["recommendation1", "recommendation2"],
    "monitoring_suggestions": ["suggestion1", "suggestion2"],
    "process_improvements": ["improvement1", "improvement2"]
}}
"""

            messages = [
                SystemMessage(
                    content="You are a data quality expert providing recommendations for improving data processes."
                ),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.agenerate([messages])
            response_text = response.generations[0][0].text

            # Parse response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "data_quality_improvements": ["Review data validation rules"],
                    "monitoring_suggestions": ["Set up automated alerts"],
                    "process_improvements": ["Implement data quality checks"],
                }

        except Exception as e:
            logger.error("Failed to generate recommendations", error=str(e))
            return {
                "data_quality_improvements": ["Review data validation rules"],
                "monitoring_suggestions": ["Set up automated alerts"],
                "process_improvements": ["Implement data quality checks"],
            }
