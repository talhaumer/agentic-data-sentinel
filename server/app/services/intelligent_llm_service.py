"""Enhanced LLM service with intelligent reasoning capabilities."""

from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import pandas as pd
import numpy as np
import aiohttp
from ..core.config import get_settings
from ..utils.json_encoder import custom_jsonable_encoder
import structlog

logger = structlog.get_logger(__name__)


class IntelligentLLMService:
    """Enhanced LLM service with advanced reasoning capabilities."""
    
    def __init__(self):
        self.settings = get_settings()
        self.conversation_history = []
        self.learning_memory = {}
    
    async def analyze_data_quality(self, data: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to intelligently analyze data quality patterns."""
        try:
            # Check if data is None or empty
            if data is None or data.empty:
                return {
                    "error": "No data available for analysis",
                    "analysis": "Cannot analyze empty dataset",
                    "recommendations": ["Ensure data is loaded before analysis"],
                    "confidence": 0.0
                }
            
            # Prepare data summary for LLM
            data_summary = self._prepare_data_summary(data)
            
            prompt = f"""
            As an expert data quality analyst, analyze this dataset and provide intelligent insights:
            
            Dataset Summary:
            - Rows: {data_summary['rows']}
            - Columns: {data_summary['columns']}
            - Data Types: {data_summary['data_types']}
            - Missing Values: {data_summary['missing_values']}
            - Sample Data: {data_summary['sample_data']}
            
            Context: {context}
            
            Please provide:
            1. Potential data quality issues you can identify
            2. Recommended validation rules based on data patterns
            3. Risk assessment for each column
            4. Suggested anomaly detection strategies
            5. Business impact analysis
            
            Respond in JSON format with detailed analysis.
            """
            
            response = await self._call_llm(prompt)
            return self._parse_llm_response(response)
            
        except Exception as e:
            logger.error("Data quality analysis failed", error=str(e))
            return {"error": str(e)}
    
    async def generate_dynamic_rules(self, data: pd.DataFrame, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate dynamic validation rules based on data characteristics."""
        try:
            prompt = f"""
            Generate intelligent validation rules for this dataset:
            
            Data Characteristics:
            - Shape: {data.shape}
            - Columns: {list(data.columns)}
            - Data Types: {data.dtypes.to_dict()}
            - Value Ranges: {self._get_value_ranges(data)}
            
            Context: {context}
            
            Create validation rules that are:
            1. Appropriate for the data type and domain
            2. Statistically sound
            3. Business-relevant
            4. Adaptive to data patterns
            
            Return as JSON array of rule objects with: rule_type, column, condition, threshold, severity
            """
            
            response = await self._call_llm(prompt)
            return self._parse_rules_response(response)
            
        except Exception as e:
            logger.error("Dynamic rule generation failed", error=str(e))
            return []
    
    async def calculate_optimal_thresholds(self, data: pd.DataFrame, column: str) -> Dict[str, float]:
        """Calculate optimal thresholds for anomaly detection."""
        try:
            column_data = data[column].dropna()
            
            prompt = f"""
            Calculate optimal statistical thresholds for anomaly detection in column '{column}':
            
            Column Statistics:
            - Mean: {column_data.mean()}
            - Std: {column_data.std()}
            - Min: {column_data.min()}
            - Max: {column_data.max()}
            - Quartiles: {column_data.quantile([0.25, 0.5, 0.75]).to_dict()}
            
            Provide thresholds for:
            1. Mild outliers (1.5 * IQR)
            2. Severe outliers (3 * IQR)
            3. Statistical significance (z-score > 2)
            4. Domain-specific thresholds based on data characteristics
            
            Return as JSON with threshold values and reasoning.
            """
            
            response = await self._call_llm(prompt)
            return self._parse_thresholds_response(response)
            
        except Exception as e:
            logger.error("Threshold calculation failed", error=str(e))
            return {}
    
    async def reason_about_anomalies(self, anomalies: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to reason about detected anomalies and provide insights."""
        try:
            prompt = f"""
            Analyze these detected anomalies and provide intelligent reasoning:
            
            Anomalies: {json.dumps(anomalies, indent=2)}
            Context: {context}
            
            Please provide:
            1. Root cause analysis for each anomaly
            2. Potential business impact
            3. Recommended remediation strategies
            4. Prevention measures
            5. Priority ranking based on severity and impact
            
            Consider patterns across anomalies and provide holistic insights.
            """
            
            response = await self._call_llm(prompt)
            return self._parse_anomaly_analysis(response)
            
        except Exception as e:
            logger.error("Anomaly reasoning failed", error=str(e))
            return {"error": str(e)}
    
    async def learn_from_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from user feedback and improve future recommendations."""
        try:
            # Store feedback in learning memory
            feedback_id = f"feedback_{datetime.utcnow().timestamp()}"
            self.learning_memory[feedback_id] = {
                "feedback": feedback,
                "timestamp": datetime.utcnow().isoformat(),
                "learned_patterns": await self._extract_learning_patterns(feedback)
            }
            
            # Update agent behavior based on feedback
            await self._update_agent_behavior(feedback)
            
            return {"status": "learned", "feedback_id": feedback_id}
            
        except Exception as e:
            logger.error("Learning from feedback failed", error=str(e))
            return {"error": str(e)}
    
    async def suggest_workflow_optimization(self, workflow_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Suggest workflow optimizations based on execution history."""
        try:
            prompt = f"""
            Analyze this workflow execution history and suggest optimizations:
            
            History: {json.dumps(workflow_history, indent=2)}
            
            Suggest:
            1. Workflow bottlenecks and inefficiencies
            2. Opportunities for parallel execution
            3. Agent performance improvements
            4. Resource optimization strategies
            5. Workflow restructuring recommendations
            
            Focus on making the system more efficient and intelligent.
            """
            
            response = await self._call_llm(prompt)
            return self._parse_optimization_suggestions(response)
            
        except Exception as e:
            logger.error("Workflow optimization failed", error=str(e))
            return {"error": str(e)}
    
    def _prepare_data_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Prepare a comprehensive data summary for LLM analysis."""
        # Convert data types to strings to avoid JSON serialization issues
        data_types = {}
        for col, dtype in data.dtypes.to_dict().items():
            data_types[col] = str(dtype)
        
        # Convert missing values to regular Python int
        missing_values = {}
        for col, count in data.isnull().sum().to_dict().items():
            missing_values[col] = int(count)
        
        # Convert statistical summary to JSON-serializable format
        statistical_summary = {}
        try:
            desc = data.describe()
            for col in desc.columns:
                statistical_summary[col] = {}
                for stat in desc.index:
                    value = desc.loc[stat, col]
                    if pd.isna(value):
                        statistical_summary[col][stat] = None
                    else:
                        # Convert numpy types to Python types
                        if hasattr(value, 'item'):
                            statistical_summary[col][stat] = value.item()
                        else:
                            statistical_summary[col][stat] = float(value)
        except Exception:
            statistical_summary = {}
        
        # Convert sample data to JSON-serializable format
        sample_data = []
        try:
            for record in data.head(3).to_dict('records'):
                serializable_record = {}
                for key, value in record.items():
                    if pd.isna(value):
                        serializable_record[key] = None
                    elif hasattr(value, 'item'):  # numpy scalar
                        serializable_record[key] = value.item()
                    elif isinstance(value, (np.integer, np.floating)):
                        serializable_record[key] = value.item()
                    else:
                        serializable_record[key] = value
                sample_data.append(serializable_record)
        except Exception:
            sample_data = []
        
        # Use custom encoder to ensure all data is JSON-serializable
        summary = {
            "rows": int(len(data)),
            "columns": int(len(data.columns)),
            "data_types": data_types,
            "missing_values": missing_values,
            "sample_data": sample_data,
            "statistical_summary": statistical_summary
        }
        
        return custom_jsonable_encoder(summary)
    
    def _get_value_ranges(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get value ranges for numerical columns."""
        ranges = {}
        for col in data.select_dtypes(include=['number']).columns:
            min_val = data[col].min()
            max_val = data[col].max()
            range_val = max_val - min_val
            
            # Convert numpy types to Python types
            ranges[col] = {
                "min": min_val.item() if hasattr(min_val, 'item') else float(min_val),
                "max": max_val.item() if hasattr(max_val, 'item') else float(max_val),
                "range": range_val.item() if hasattr(range_val, 'item') else float(range_val)
            }
        return custom_jsonable_encoder(ranges)
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        settings = get_settings()
        
        # Check if we have API key configured (try both new and legacy formats)
        api_key = settings.llm_api_key
        if not api_key and settings.llm_provider.lower() == "openai":
            api_key = settings.openai_api_key
        elif not api_key and settings.llm_provider.lower() == "groq":
            api_key = settings.groq_api_key
            
        if not api_key:
            logger.warning("No LLM API key configured, using mock response")
            return self._get_mock_response()
        
        # Call the configured LLM provider
        try:
            if settings.llm_provider.lower() == "openai":
                return await self._call_openai(prompt, api_key, settings)
            elif settings.llm_provider.lower() == "groq":
                return await self._call_groq(prompt, api_key, settings)
            else:
                logger.warning(f"Unknown LLM provider: {settings.llm_provider}, using mock response")
                return self._get_mock_response()
        except Exception as e:
            logger.warning(f"LLM call failed, using mock response", error=str(e))
            return self._get_mock_response()
    
    async def _call_openai(self, prompt: str, api_key: str, settings) -> str:
        """Call OpenAI API."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": settings.llm_model,  # Use configured model
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert data quality analyst. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error {response.status}: {error_text}")
    
    async def _call_groq(self, prompt: str, api_key: str, settings) -> str:
        """Call Groq API."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": settings.llm_model,  # Use configured model
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert data quality analyst. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise Exception(f"Groq API error {response.status}: {error_text}")
    
    def _get_mock_response(self) -> str:
        """Get mock response when no LLM is available."""
        return json.dumps({
            "analysis": "Mock LLM analysis - No API key configured",
            "recommendations": ["Mock recommendation 1", "Mock recommendation 2"],
            "confidence": 0.85,
            "rules": [
                {
                    "rule_type": "range_check",
                    "column": "value",
                    "condition": "between",
                    "threshold": [0, 100],
                    "severity": "medium"
                }
            ],
            "thresholds": {
                "mild_outliers": 1.5,
                "severe_outliers": 3.0,
                "z_score_threshold": 2.0
            },
            "anomaly_analysis": {
                "root_causes": ["Data entry error", "System issue"],
                "business_impact": "medium",
                "recommendations": ["Review data collection process"],
                "priority_ranking": "high"
            },
            "optimization_suggestions": {
                "bottlenecks": ["Sequential processing"],
                "parallel_opportunities": ["Validation and anomaly detection"],
                "performance_improvements": ["Caching", "Batch processing"]
            }
        })
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured data."""
        try:
            return json.loads(response)
        except:
            return {"raw_response": response}
    
    def _parse_rules_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse rules response into structured data."""
        try:
            data = json.loads(response)
            return data.get("rules", [])
        except:
            return []
    
    def _parse_thresholds_response(self, response: str) -> Dict[str, float]:
        """Parse thresholds response into structured data."""
        try:
            data = json.loads(response)
            return data.get("thresholds", {})
        except:
            return {}
    
    def _parse_anomaly_analysis(self, response: str) -> Dict[str, Any]:
        """Parse anomaly analysis response."""
        try:
            if not response or not isinstance(response, str):
                return {"error": "Invalid response", "raw_response": str(response)}
            
            data = json.loads(response)
            if isinstance(data, dict):
                return data.get("anomaly_analysis", {"raw_response": response})
            else:
                return {"raw_response": response}
        except json.JSONDecodeError:
            return {"raw_response": response, "parse_error": "Failed to parse JSON"}
        except Exception as e:
            return {"error": str(e), "raw_response": response}
    
    def _parse_optimization_suggestions(self, response: str) -> Dict[str, Any]:
        """Parse optimization suggestions response."""
        try:
            data = json.loads(response)
            return data.get("optimization_suggestions", {"raw_response": response})
        except:
            return {"raw_response": response}
    
    async def _extract_learning_patterns(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Extract learning patterns from feedback."""
        # Implement pattern extraction logic
        return {"patterns": []}
    
    async def _update_agent_behavior(self, feedback: Dict[str, Any]) -> None:
        """Update agent behavior based on feedback."""
        # Implement behavior update logic
        pass
