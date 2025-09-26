"""LLM service for generating explanations."""

import structlog
from typing import Any, Dict, List, Optional

from app.core.config import get_settings

logger = structlog.get_logger(__name__)


class LLMService:
    """Service for LLM-powered explanations and recommendations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm_available = True
        
        # Initialize LLM based on provider
        try:
            if self.settings.llm_provider.lower() == "groq":
                from langchain_groq import ChatGroq
                self.llm = ChatGroq(
                    model_name=self.settings.llm_model,
                    groq_api_key=self.settings.llm_api_key,
                    temperature=0.1,
                    max_tokens=1000,
                )
            else:  # Default to OpenAI
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model_name=self.settings.llm_model,
                    openai_api_key=self.settings.llm_api_key,
                    temperature=0.1,
                    max_tokens=1000,
                )
        except Exception as e:
            logger.warning("LLM initialization failed", error=str(e))
            self.llm_available = False
    
    async def generate_explanation(self, prompt: str) -> str:
        """Generate explanation using LLM."""
        if not self.llm_available:
            return "LLM service not available"
        
        try:
            from langchain.schema import HumanMessage
            response = await self.llm.ainvoke([
                HumanMessage(content=prompt)
            ])
            return response.content
        except Exception as e:
            logger.error("LLM explanation failed", error=str(e))
            return f"Failed to generate explanation: {str(e)}"
    
    async def generate_recommendations(self, anomaly_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations for an anomaly."""
        if not self.llm_available:
            return ["LLM service not available for recommendations"]
        
        prompt = f"""
        Based on this data quality anomaly, provide 3-5 specific recommendations:
        
        Anomaly Type: {anomaly_data.get('type', 'Unknown')}
        Description: {anomaly_data.get('description', 'No description')}
        Severity: {anomaly_data.get('severity', 'Unknown')}
        
        Provide actionable recommendations to fix this issue.
        """
        
        try:
            explanation = await self.generate_explanation(prompt)
            # Parse explanation into list of recommendations
            recommendations = [
                line.strip() 
                for line in explanation.split('\n') 
                if line.strip()
            ]
            return recommendations[:5]  # Limit to 5 recommendations
        except Exception as e:
            logger.error("Recommendation generation failed", error=str(e))
            return ["Failed to generate recommendations"]
