"""Enhanced Validation Agent with intelligent reasoning capabilities."""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from .base_agent import BaseAgent, AgentContext, AgentResult, AgentStatus, Priority
from ..services.intelligent_llm_service import IntelligentLLMService
import structlog

logger = structlog.get_logger(__name__)


class IntelligentValidationAgent(BaseAgent):
    """Enhanced validation agent with AI-powered reasoning and dynamic rule generation."""
    
    def __init__(self):
        super().__init__(
            name="intelligent_validation_agent",
            description="AI-powered data validation with dynamic rule generation and intelligent reasoning"
        )
        self.llm_service = IntelligentLLMService()
        self.validation_rules = []
        self.learning_memory = {}
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if agent can handle the context."""
        return context.dataset_id is not None and hasattr(context, 'loaded_data')
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute intelligent data validation."""
        try:
            # Get loaded data from context
            loaded_data = getattr(context, 'loaded_data', None)
            if loaded_data is None:
                return AgentResult(
                    agent_name=self.name,
                    status=AgentStatus.FAILED,
                    error="No data available for validation"
                )
            
            # Step 1: AI-powered data analysis
            logger.info("Starting intelligent data analysis")
            data_analysis = await self.llm_service.analyze_data_quality(loaded_data, {
                "dataset_id": context.dataset_id,
                "dataset_name": context.dataset_name,
                "validation_context": "comprehensive_quality_check"
            })
            
            # Ensure data_analysis is a dictionary
            if isinstance(data_analysis, str):
                data_analysis = {"analysis": data_analysis, "recommendations": []}
            elif not isinstance(data_analysis, dict):
                data_analysis = {"analysis": str(data_analysis), "recommendations": []}
            
            # Step 2: Generate dynamic validation rules
            logger.info("Generating dynamic validation rules")
            dynamic_rules = await self.llm_service.generate_dynamic_rules(loaded_data, {
                "dataset_id": context.dataset_id,
                "analysis": data_analysis
            })
            
            # Step 3: Execute comprehensive validation
            logger.info("Executing comprehensive validation")
            validation_results = await self._execute_comprehensive_validation(loaded_data, dynamic_rules)
            
            # Step 4: Intelligent anomaly reasoning
            logger.info("Analyzing validation results with AI")
            anomaly_analysis = await self.llm_service.reason_about_anomalies(
                validation_results.get('anomalies', []),
                {
                    "dataset_id": context.dataset_id,
                    "validation_rules": dynamic_rules,
                    "data_analysis": data_analysis
                }
            )
            
            # Step 5: Generate intelligent recommendations
            recommendations = await self._generate_intelligent_recommendations(
                validation_results, anomaly_analysis, data_analysis
            )
            
            # Step 6: Learn from this validation session
            await self._learn_from_validation_session(validation_results, anomaly_analysis)
            
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "validation_results": validation_results,
                    "anomaly_analysis": anomaly_analysis,
                    "data_analysis": data_analysis,
                    "dynamic_rules": dynamic_rules,
                    "recommendations": recommendations,
                    "validation_confidence": self._calculate_validation_confidence(validation_results)
                },
                confidence=0.95,
                recommendations=recommendations,
                next_actions=[
                    "trigger_anomaly_detection_agent",
                    "update_validation_rules",
                    "store_learning_insights"
                ]
            )
            
        except Exception as e:
            logger.error("Intelligent validation failed", error=str(e))
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                data={},
                error=str(e)
            )
    
    async def _execute_comprehensive_validation(self, data: pd.DataFrame, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute comprehensive validation with multiple techniques."""
        validation_results = {
            "basic_checks": await self._basic_data_quality_checks(data),
            "statistical_validation": await self._statistical_validation(data),
            "pattern_validation": await self._pattern_validation(data),
            "rule_based_validation": await self._rule_based_validation(data, rules),
            "anomalies": [],
            "overall_score": 0.0
        }
        
        # Combine all validation results
        all_anomalies = []
        for check_type, results in validation_results.items():
            if isinstance(results, dict) and 'anomalies' in results:
                all_anomalies.extend(results['anomalies'])
        
        validation_results['anomalies'] = all_anomalies
        validation_results['overall_score'] = self._calculate_overall_score(validation_results)
        
        return validation_results
    
    async def _basic_data_quality_checks(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform basic data quality checks."""
        checks = {
            "missing_values": data.isnull().sum().to_dict(),
            "duplicate_rows": data.duplicated().sum(),
            "empty_columns": [col for col in data.columns if data[col].isnull().all()],
            "data_type_consistency": self._check_data_type_consistency(data),
            "anomalies": []
        }
        
        # Identify anomalies
        if checks["duplicate_rows"] > 0:
            checks["anomalies"].append({
                "type": "duplicate_rows",
                "severity": "medium",
                "count": checks["duplicate_rows"],
                "description": f"Found {checks['duplicate_rows']} duplicate rows"
            })
        
        if checks["empty_columns"]:
            checks["anomalies"].append({
                "type": "empty_columns",
                "severity": "high",
                "columns": checks["empty_columns"],
                "description": f"Found {len(checks['empty_columns'])} completely empty columns"
            })
        
        return checks
    
    async def _statistical_validation(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform statistical validation."""
        results = {
            "outliers": {},
            "distribution_analysis": {},
            "anomalies": []
        }
        
        for column in data.select_dtypes(include=[np.number]).columns:
            # Z-score based outlier detection
            z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
            outliers = data[z_scores > 3]
            
            if len(outliers) > 0:
                results["outliers"][column] = len(outliers)
                results["anomalies"].append({
                    "type": "statistical_outliers",
                    "severity": "medium",
                    "column": column,
                    "count": len(outliers),
                    "description": f"Found {len(outliers)} statistical outliers in {column}"
                })
        
        return results
    
    async def _pattern_validation(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform pattern-based validation."""
        results = {
            "pattern_violations": {},
            "anomalies": []
        }
        
        # Check for unexpected patterns
        for column in data.columns:
            if data[column].dtype == 'object':
                # Check for unexpected string patterns
                unique_values = data[column].value_counts()
                if len(unique_values) == 1:
                    results["pattern_violations"][column] = "constant_value"
                    results["anomalies"].append({
                        "type": "constant_value",
                        "severity": "low",
                        "column": column,
                        "description": f"Column {column} has only one unique value"
                    })
        
        return results
    
    async def _rule_based_validation(self, data: pd.DataFrame, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute rule-based validation."""
        results = {
            "rule_violations": [],
            "anomalies": []
        }
        
        for rule in rules:
            try:
                violations = await self._apply_validation_rule(data, rule)
                if violations:
                    results["rule_violations"].extend(violations)
                    results["anomalies"].extend(violations)
            except Exception as e:
                logger.warning(f"Failed to apply rule {rule.get('rule_type')}", error=str(e))
        
        return results
    
    async def _apply_validation_rule(self, data: pd.DataFrame, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply a single validation rule."""
        violations = []
        rule_type = rule.get('rule_type')
        column = rule.get('column')
        condition = rule.get('condition')
        threshold = rule.get('threshold')
        severity = rule.get('severity', 'medium')
        
        if column not in data.columns:
            return violations
        
        try:
            if rule_type == "range_check":
                if condition == "between":
                    min_val, max_val = threshold
                    violations_data = data[(data[column] < min_val) | (data[column] > max_val)]
                elif condition == "greater_than":
                    violations_data = data[data[column] <= threshold]
                elif condition == "less_than":
                    violations_data = data[data[column] >= threshold]
                
                if len(violations_data) > 0:
                    violations.append({
                        "type": "range_violation",
                        "severity": severity,
                        "column": column,
                        "count": len(violations_data),
                        "description": f"Range violation in {column}: {len(violations_data)} records"
                    })
            
            elif rule_type == "null_check":
                null_count = data[column].isnull().sum()
                if null_count > threshold:
                    violations.append({
                        "type": "null_violation",
                        "severity": severity,
                        "column": column,
                        "count": null_count,
                        "description": f"Too many null values in {column}: {null_count} records"
                    })
            
            elif rule_type == "pattern_check":
                pattern = rule.get('pattern')
                if pattern:
                    violations_data = data[~data[column].astype(str).str.match(pattern, na=False)]
                    if len(violations_data) > 0:
                        violations.append({
                            "type": "pattern_violation",
                            "severity": severity,
                            "column": column,
                            "count": len(violations_data),
                            "description": f"Pattern violation in {column}: {len(violations_data)} records"
                        })
        
        except Exception as e:
            logger.warning(f"Error applying rule {rule_type} to column {column}", error=str(e))
        
        return violations
    
    def _check_data_type_consistency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check for data type consistency issues."""
        issues = {}
        for column in data.columns:
            if data[column].dtype == 'object':
                # Check if numeric data is stored as strings
                try:
                    pd.to_numeric(data[column], errors='raise')
                    issues[column] = "numeric_as_string"
                except:
                    pass
        return issues
    
    def _calculate_overall_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate overall validation score."""
        total_anomalies = len(validation_results.get('anomalies', []))
        total_records = validation_results.get('basic_checks', {}).get('total_records', 1)
        
        # Base score
        score = 1.0
        
        # Deduct points for anomalies
        anomaly_penalty = min(total_anomalies * 0.1, 0.5)
        score -= anomaly_penalty
        
        # Deduct points for high severity issues
        high_severity_count = sum(1 for anomaly in validation_results.get('anomalies', []) 
                                if anomaly.get('severity') == 'high')
        severity_penalty = min(high_severity_count * 0.2, 0.3)
        score -= severity_penalty
        
        return max(score, 0.0)
    
    def _calculate_validation_confidence(self, validation_results: Dict[str, Any]) -> float:
        """Calculate confidence in validation results."""
        overall_score = validation_results.get('overall_score', 0.0)
        anomaly_count = len(validation_results.get('anomalies', []))
        
        # Higher confidence for higher scores and fewer anomalies
        confidence = overall_score * (1 - min(anomaly_count * 0.05, 0.3))
        return max(confidence, 0.1)
    
    async def _generate_intelligent_recommendations(self, validation_results: Dict[str, Any], 
                                                  anomaly_analysis: Dict[str, Any], 
                                                  data_analysis: Dict[str, Any]) -> List[str]:
        """Generate intelligent recommendations based on validation results."""
        recommendations = []
        
        # Based on validation score
        overall_score = validation_results.get('overall_score', 0.0)
        if overall_score < 0.7:
            recommendations.append("Data quality is below acceptable standards - immediate attention required")
        elif overall_score < 0.85:
            recommendations.append("Data quality needs improvement - consider data cleaning")
        else:
            recommendations.append("Data quality is good - maintain current standards")
        
        # Based on anomaly analysis
        if anomaly_analysis.get('high_priority_issues'):
            recommendations.append("Address high-priority anomalies immediately")
        
        if anomaly_analysis.get('systematic_issues'):
            recommendations.append("Investigate systematic data quality issues")
        
        # Based on data analysis
        if data_analysis.get('missing_data_patterns'):
            recommendations.append("Implement data collection improvements to reduce missing values")
        
        return recommendations
    
    async def _learn_from_validation_session(self, validation_results: Dict[str, Any], 
                                           anomaly_analysis: Dict[str, Any]) -> None:
        """Learn from validation session to improve future validations."""
        session_id = f"validation_{datetime.utcnow().timestamp()}"
        
        self.learning_memory[session_id] = {
            "timestamp": datetime.utcnow().isoformat(),
            "validation_results": validation_results,
            "anomaly_analysis": anomaly_analysis,
            "learned_patterns": self._extract_learning_patterns(validation_results)
        }
        
        # Update validation rules based on learning
        await self._update_validation_rules_from_learning()
    
    def _extract_learning_patterns(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract learning patterns from validation results."""
        patterns = {
            "common_anomaly_types": {},
            "effective_rules": [],
            "ineffective_rules": []
        }
        
        # Analyze anomaly types
        for anomaly in validation_results.get('anomalies', []):
            anomaly_type = anomaly.get('type', 'unknown')
            patterns["common_anomaly_types"][anomaly_type] = patterns["common_anomaly_types"].get(anomaly_type, 0) + 1
        
        return patterns
    
    async def _update_validation_rules_from_learning(self) -> None:
        """Update validation rules based on learning patterns."""
        # Implement rule update logic based on learning memory
        pass
