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
        self.llm_available = True

        # Initialize LLM based on provider
        try:
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
        except Exception as e:
            logger.error("Failed to initialize LLM", error=str(e))
            self.llm_available = False
            self.llm = None

    async def explain_anomaly(
        self, anomaly: Anomaly, context: Optional[Dict[str, Any]] = None
    ) -> LLMExplanationResponse:
        """Generate LLM explanation for an anomaly."""
        # Check if LLM is available
        if not self.llm_available or self.llm is None:
            logger.warning("LLM not available, using fallback explanation", anomaly_id=anomaly.id)
            return LLMExplanationResponse(
                explanation=self._generate_fallback_explanation(anomaly),
                confidence=0.3,
                suggested_sql=self._generate_fallback_sql(anomaly),
                action_type=self._suggest_fallback_action(anomaly),
            )

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
            # Return meaningful fallback explanation based on anomaly type
            fallback_explanation = self._generate_fallback_explanation(anomaly)
            return LLMExplanationResponse(
                explanation=fallback_explanation,
                confidence=0.3,
                suggested_sql=self._generate_fallback_sql(anomaly),
                action_type=self._suggest_fallback_action(anomaly),
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

    def _generate_fallback_explanation(self, anomaly: Anomaly) -> str:
        """Generate a meaningful fallback explanation when LLM fails."""
        issue_type = anomaly.issue_type.lower()
        column_name = anomaly.column_name or "unknown column"
        severity = anomaly.severity
        
        explanations = {
            "uniqueness": f"This {issue_type} anomaly in column '{column_name}' indicates low data diversity. This commonly occurs when data contains many duplicate values, categorical data with limited options, or when data generation processes create repetitive patterns. For severity {severity}/5, this suggests the data may not be suitable for certain analytical purposes that require unique identifiers.",
            
            "null_values": f"This {issue_type} anomaly in column '{column_name}' indicates missing data. This can occur due to incomplete data collection, ETL failures, or optional fields not being populated. For severity {severity}/5, this may impact data completeness and analysis accuracy.",
            
            "completeness": f"This {issue_type} anomaly in column '{column_name}' suggests incomplete data records. This typically happens when required fields are not being populated during data ingestion or when data sources have gaps. For severity {severity}/5, this may affect data reliability.",
            
            "consistency": f"This {issue_type} anomaly in column '{column_name}' indicates data format inconsistencies. This often occurs when data comes from multiple sources with different standards, or when data transformation rules are not properly applied. For severity {severity}/5, this may cause processing issues.",
            
            "accuracy": f"This {issue_type} anomaly in column '{column_name}' suggests data accuracy issues. This can happen when data validation rules fail, data entry errors occur, or when data becomes stale. For severity {severity}/5, this may impact business decisions.",
        }
        
        return explanations.get(issue_type, f"This {issue_type} anomaly in column '{column_name}' with severity {severity}/5 requires investigation. The specific root cause should be determined by examining the data source and processing pipeline.")

    def _generate_fallback_sql(self, anomaly: Anomaly) -> str:
        """Generate fallback SQL for investigation."""
        column_name = anomaly.column_name or "column_name"
        table_name = anomaly.table_name or "table_name"
        issue_type = anomaly.issue_type.lower()
        
        sql_queries = {
            "uniqueness": f"SELECT {column_name}, COUNT(*) as frequency FROM {table_name} GROUP BY {column_name} ORDER BY frequency DESC LIMIT 10;",
            "null_values": f"SELECT COUNT(*) as total_rows, COUNT({column_name}) as non_null_count, COUNT(*) - COUNT({column_name}) as null_count FROM {table_name};",
            "completeness": f"SELECT COUNT(*) as total_rows, COUNT({column_name}) as complete_count, ROUND(COUNT({column_name}) * 100.0 / COUNT(*), 2) as completeness_percentage FROM {table_name};",
            "consistency": f"SELECT {column_name}, COUNT(*) as frequency FROM {table_name} WHERE {column_name} IS NOT NULL GROUP BY {column_name} ORDER BY frequency DESC LIMIT 20;",
            "accuracy": f"SELECT {column_name}, COUNT(*) as frequency FROM {table_name} WHERE {column_name} IS NOT NULL GROUP BY {column_name} ORDER BY frequency DESC LIMIT 10;",
        }
        
        return sql_queries.get(issue_type, f"SELECT * FROM {table_name} WHERE {column_name} IS NOT NULL LIMIT 10;")

    def _suggest_fallback_action(self, anomaly: Anomaly) -> str:
        """Suggest fallback action based on anomaly severity and type."""
        severity = anomaly.severity
        issue_type = anomaly.issue_type.lower()
        
        # High severity anomalies should be investigated
        if severity >= 4:
            return "create_issue"
        elif severity >= 3:
            return "notify_owner"
        elif severity >= 2:
            return "auto_fix"
        else:
            return "no_action"
