"""Enhanced Anomaly Detection Agent with AI-powered reasoning and adaptive thresholds."""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from .base_agent import BaseAgent, AgentContext, AgentResult, AgentStatus, Priority
from ..services.intelligent_llm_service import IntelligentLLMService
import structlog

logger = structlog.get_logger(__name__)


class IntelligentAnomalyDetectionAgent(BaseAgent):
    """Enhanced anomaly detection agent with AI-powered reasoning and adaptive learning."""
    
    def __init__(self):
        super().__init__(
            name="intelligent_anomaly_detection_agent",
            description="AI-powered anomaly detection with adaptive thresholds and intelligent reasoning"
        )
        self.llm_service = IntelligentLLMService()
        self.anomaly_models = {}
        self.learning_memory = {}
        self.adaptive_thresholds = {}
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if agent can handle the context."""
        return context.dataset_id is not None and hasattr(context, 'loaded_data')
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute intelligent anomaly detection."""
        try:
            # Get loaded data from context
            loaded_data = getattr(context, 'loaded_data', None)
            if loaded_data is None:
                return AgentResult(
                    agent_name=self.name,
                    status=AgentStatus.FAILED,
                    error="No data available for anomaly detection"
                )
            
            # Step 1: AI-powered data analysis for anomaly detection
            logger.info("Starting intelligent anomaly analysis")
            anomaly_analysis = await self.llm_service.analyze_data_quality(loaded_data, {
                "dataset_id": context.dataset_id,
                "dataset_name": context.dataset_name,
                "analysis_type": "anomaly_detection",
                "focus": "outlier_patterns"
            })
            
            # Ensure anomaly_analysis is a dictionary
            if isinstance(anomaly_analysis, str):
                anomaly_analysis = {"analysis": anomaly_analysis, "recommendations": []}
            elif not isinstance(anomaly_analysis, dict):
                anomaly_analysis = {"analysis": str(anomaly_analysis), "recommendations": []}
            
            # Step 2: Calculate adaptive thresholds
            logger.info("Calculating adaptive thresholds")
            adaptive_thresholds = await self._calculate_adaptive_thresholds(loaded_data, anomaly_analysis)
            
            # Step 3: Multi-method anomaly detection
            logger.info("Executing multi-method anomaly detection")
            detection_results = await self._execute_multi_method_detection(loaded_data, adaptive_thresholds)
            
            # Step 4: AI-powered anomaly reasoning
            logger.info("Analyzing anomalies with AI reasoning")
            intelligent_analysis = await self.llm_service.reason_about_anomalies(
                detection_results.get('anomalies', []),
                {
                    "dataset_id": context.dataset_id,
                    "detection_methods": detection_results.get('methods_used', []),
                    "thresholds": adaptive_thresholds,
                    "data_analysis": anomaly_analysis
                }
            )
            
            # Ensure intelligent_analysis is a dictionary
            if not isinstance(intelligent_analysis, dict):
                intelligent_analysis = {"raw_analysis": str(intelligent_analysis)}
            
            # Step 5: Generate intelligent recommendations
            recommendations = await self._generate_anomaly_recommendations(
                detection_results, intelligent_analysis, anomaly_analysis
            )
            
            # Step 6: Learn from detection session
            await self._learn_from_detection_session(detection_results, intelligent_analysis)
            
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "detection_results": detection_results,
                    "intelligent_analysis": intelligent_analysis,
                    "adaptive_thresholds": adaptive_thresholds,
                    "anomaly_analysis": anomaly_analysis,
                    "recommendations": recommendations,
                    "detection_confidence": self._calculate_detection_confidence(detection_results)
                },
                confidence=0.92,
                recommendations=recommendations,
                next_actions=[
                    "trigger_remediation_agent",
                    "update_anomaly_models",
                    "store_learning_insights"
                ]
            )
            
        except Exception as e:
            logger.error("Intelligent anomaly detection failed", error=str(e))
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                data={},
                error=str(e)
            )
    
    async def _calculate_adaptive_thresholds(self, data: pd.DataFrame, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate adaptive thresholds for anomaly detection."""
        thresholds = {}
        
        for column in data.select_dtypes(include=[np.number]).columns:
            try:
                # Get AI-suggested thresholds
                ai_thresholds = await self.llm_service.calculate_optimal_thresholds(data, column)
                
                # Ensure ai_thresholds is a dictionary
                if isinstance(ai_thresholds, str):
                    ai_thresholds = {}
                elif not isinstance(ai_thresholds, dict):
                    ai_thresholds = {}
                
                # Calculate statistical thresholds
                stat_thresholds = self._calculate_statistical_thresholds(data[column])
                
                # Combine AI and statistical thresholds
                thresholds[column] = {
                    "ai_thresholds": ai_thresholds,
                    "statistical_thresholds": stat_thresholds,
                    "final_thresholds": self._combine_thresholds(ai_thresholds, stat_thresholds)
                }
                
            except Exception as e:
                logger.warning(f"Failed to calculate thresholds for column {column}", error=str(e))
                thresholds[column] = self._calculate_statistical_thresholds(data[column])
        
        return thresholds
    
    def _calculate_statistical_thresholds(self, series: pd.Series) -> Dict[str, float]:
        """Calculate statistical thresholds for anomaly detection."""
        series_clean = series.dropna()
        
        if len(series_clean) == 0:
            return {}
        
        # Z-score based thresholds
        mean_val = series_clean.mean()
        std_val = series_clean.std()
        
        # IQR based thresholds
        Q1 = series_clean.quantile(0.25)
        Q3 = series_clean.quantile(0.75)
        IQR = Q3 - Q1
        
        return {
            "z_score_2": mean_val + 2 * std_val,
            "z_score_3": mean_val + 3 * std_val,
            "iqr_mild": Q3 + 1.5 * IQR,
            "iqr_severe": Q3 + 3 * IQR,
            "percentile_95": series_clean.quantile(0.95),
            "percentile_99": series_clean.quantile(0.99)
        }
    
    def _combine_thresholds(self, ai_thresholds: Dict[str, Any], stat_thresholds: Dict[str, float]) -> Dict[str, float]:
        """Combine AI and statistical thresholds intelligently."""
        combined = {}
        
        # Use AI thresholds if available, otherwise fall back to statistical
        for key in stat_thresholds:
            if key in ai_thresholds and isinstance(ai_thresholds[key], (int, float)):
                combined[key] = ai_thresholds[key]
            else:
                combined[key] = stat_thresholds[key]
        
        return combined
    
    async def _execute_multi_method_detection(self, data: pd.DataFrame, thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple anomaly detection methods."""
        results = {
            "statistical_anomalies": await self._statistical_anomaly_detection(data, thresholds),
            "isolation_forest_anomalies": await self._isolation_forest_detection(data),
            "clustering_anomalies": await self._clustering_anomaly_detection(data),
            "pattern_anomalies": await self._pattern_anomaly_detection(data),
            "temporal_anomalies": await self._temporal_anomaly_detection(data),
            "methods_used": [],
            "anomalies": []
        }
        
        # Combine all anomalies
        all_anomalies = []
        for method, anomalies in results.items():
            if isinstance(anomalies, list) and anomalies:
                all_anomalies.extend(anomalies)
                results["methods_used"].append(method)
        
        # Deduplicate and rank anomalies
        results["anomalies"] = self._deduplicate_and_rank_anomalies(all_anomalies)
        
        return results
    
    async def _statistical_anomaly_detection(self, data: pd.DataFrame, thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical methods."""
        anomalies = []
        
        for column in data.select_dtypes(include=[np.number]).columns:
            if column not in thresholds:
                continue
            
            column_data = data[column].dropna()
            if len(column_data) == 0:
                continue
            
            column_thresholds = thresholds[column].get('final_thresholds', {})
            
            # Z-score based detection
            z_scores = np.abs((column_data - column_data.mean()) / column_data.std())
            z_anomalies = column_data[z_scores > 2]
            
            if len(z_anomalies) > 0:
                anomalies.append({
                    "type": "statistical_z_score",
                    "severity": "medium",
                    "column": column,
                    "count": len(z_anomalies),
                    "indices": z_anomalies.index.tolist(),
                    "values": z_anomalies.tolist(),
                    "description": f"Found {len(z_anomalies)} statistical outliers in {column} using Z-score"
                })
            
            # IQR based detection
            Q1 = column_data.quantile(0.25)
            Q3 = column_data.quantile(0.75)
            IQR = Q3 - Q1
            iqr_anomalies = column_data[(column_data < Q1 - 1.5 * IQR) | (column_data > Q3 + 1.5 * IQR)]
            
            if len(iqr_anomalies) > 0:
                anomalies.append({
                    "type": "statistical_iqr",
                    "severity": "high",
                    "column": column,
                    "count": len(iqr_anomalies),
                    "indices": iqr_anomalies.index.tolist(),
                    "values": iqr_anomalies.tolist(),
                    "description": f"Found {len(iqr_anomalies)} IQR outliers in {column}"
                })
        
        return anomalies
    
    async def _isolation_forest_detection(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using Isolation Forest."""
        anomalies = []
        
        try:
            # Select numeric columns
            numeric_data = data.select_dtypes(include=[np.number])
            if numeric_data.empty:
                return anomalies
            
            # Handle missing values
            numeric_data_clean = numeric_data.fillna(numeric_data.median())
            
            # Fit Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(numeric_data_clean)
            
            # Get anomaly indices
            anomaly_indices = numeric_data_clean[anomaly_labels == -1].index.tolist()
            
            if len(anomaly_indices) > 0:
                anomalies.append({
                    "type": "isolation_forest",
                    "severity": "high",
                    "count": len(anomaly_indices),
                    "indices": anomaly_indices,
                    "description": f"Found {len(anomaly_indices)} anomalies using Isolation Forest"
                })
        
        except Exception as e:
            logger.warning("Isolation Forest detection failed", error=str(e))
        
        return anomalies
    
    async def _clustering_anomaly_detection(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using clustering methods."""
        anomalies = []
        
        try:
            # Select numeric columns
            numeric_data = data.select_dtypes(include=[np.number])
            if numeric_data.empty or len(numeric_data) < 10:
                return anomalies
            
            # Handle missing values and scale data
            numeric_data_clean = numeric_data.fillna(numeric_data.median())
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(numeric_data_clean)
            
            # Use DBSCAN for clustering
            dbscan = DBSCAN(eps=0.5, min_samples=5)
            cluster_labels = dbscan.fit_predict(scaled_data)
            
            # Points with label -1 are considered outliers
            outlier_indices = numeric_data_clean[cluster_labels == -1].index.tolist()
            
            if len(outlier_indices) > 0:
                anomalies.append({
                    "type": "clustering_outlier",
                    "severity": "medium",
                    "count": len(outlier_indices),
                    "indices": outlier_indices,
                    "description": f"Found {len(outlier_indices)} clustering outliers using DBSCAN"
                })
        
        except Exception as e:
            logger.warning("Clustering anomaly detection failed", error=str(e))
        
        return anomalies
    
    async def _pattern_anomaly_detection(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect pattern-based anomalies."""
        anomalies = []
        
        # Check for unexpected patterns in categorical data
        for column in data.select_dtypes(include=['object']).columns:
            value_counts = data[column].value_counts()
            
            # Check for unexpected value distributions
            if len(value_counts) > 1:
                # Check if one value dominates unexpectedly
                max_count = value_counts.iloc[0]
                total_count = len(data[column].dropna())
                dominance_ratio = max_count / total_count
                
                if dominance_ratio > 0.9:  # 90% dominance
                    anomalies.append({
                        "type": "pattern_dominance",
                        "severity": "low",
                        "column": column,
                        "dominant_value": value_counts.index[0],
                        "dominance_ratio": dominance_ratio,
                        "description": f"Value '{value_counts.index[0]}' dominates {column} with {dominance_ratio:.1%} frequency"
                    })
        
        return anomalies
    
    async def _temporal_anomaly_detection(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect temporal anomalies if time-based columns exist."""
        anomalies = []
        
        # Look for datetime columns
        datetime_columns = []
        for column in data.columns:
            if data[column].dtype == 'datetime64[ns]' or 'date' in column.lower() or 'time' in column.lower():
                datetime_columns.append(column)
        
        if not datetime_columns:
            return anomalies
        
        # Simple temporal anomaly detection
        for column in datetime_columns:
            try:
                if data[column].dtype != 'datetime64[ns]':
                    data[column] = pd.to_datetime(data[column], errors='coerce')
                
                # Check for gaps in time series
                sorted_data = data[column].dropna().sort_values()
                if len(sorted_data) > 1:
                    time_diffs = sorted_data.diff().dropna()
                    median_diff = time_diffs.median()
                    
                    # Find unusually large gaps
                    large_gaps = time_diffs[time_diffs > median_diff * 3]
                    
                    if len(large_gaps) > 0:
                        anomalies.append({
                            "type": "temporal_gap",
                            "severity": "medium",
                            "column": column,
                            "count": len(large_gaps),
                            "description": f"Found {len(large_gaps)} large temporal gaps in {column}"
                        })
            
            except Exception as e:
                logger.warning(f"Temporal anomaly detection failed for column {column}", error=str(e))
        
        return anomalies
    
    def _deduplicate_and_rank_anomalies(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate and rank anomalies by severity and importance."""
        if not anomalies:
            return []
        
        # Remove duplicates based on indices
        seen_indices = set()
        unique_anomalies = []
        
        for anomaly in anomalies:
            anomaly_indices = set(anomaly.get('indices', []))
            if not anomaly_indices.intersection(seen_indices):
                unique_anomalies.append(anomaly)
                seen_indices.update(anomaly_indices)
            else:
                # Merge with existing anomaly
                for existing in unique_anomalies:
                    if set(existing.get('indices', [])).intersection(anomaly_indices):
                        existing['count'] = max(existing.get('count', 0), anomaly.get('count', 0))
                        existing['description'] += f"; {anomaly.get('description', '')}"
                        break
        
        # Rank by severity
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        unique_anomalies.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 1), reverse=True)
        
        return unique_anomalies
    
    def _calculate_detection_confidence(self, detection_results: Dict[str, Any]) -> float:
        """Calculate confidence in anomaly detection results."""
        total_anomalies = len(detection_results.get('anomalies', []))
        methods_used = len(detection_results.get('methods_used', []))
        
        # Higher confidence with more methods and reasonable anomaly count
        if methods_used == 0:
            return 0.0
        
        # Base confidence from number of methods
        method_confidence = min(methods_used / 4.0, 1.0)
        
        # Adjust based on anomaly count (too many or too few reduces confidence)
        anomaly_factor = 1.0
        if total_anomalies > 100:  # Too many anomalies might indicate poor data
            anomaly_factor = 0.7
        elif total_anomalies == 0:  # No anomalies might indicate missed detection
            anomaly_factor = 0.8
        
        return method_confidence * anomaly_factor
    
    async def _generate_anomaly_recommendations(self, detection_results: Dict[str, Any], 
                                              intelligent_analysis: Dict[str, Any], 
                                              anomaly_analysis: Dict[str, Any]) -> List[str]:
        """Generate intelligent recommendations based on anomaly detection."""
        recommendations = []
        
        total_anomalies = len(detection_results.get('anomalies', []))
        
        if total_anomalies == 0:
            recommendations.append("No anomalies detected - data appears clean")
        elif total_anomalies < 10:
            recommendations.append("Few anomalies detected - review and validate if they are genuine issues")
        elif total_anomalies < 50:
            recommendations.append("Moderate number of anomalies - investigate data quality processes")
        else:
            recommendations.append("High number of anomalies - immediate data quality review required")
        
        # Method-specific recommendations
        methods_used = detection_results.get('methods_used', [])
        if 'isolation_forest' in methods_used:
            recommendations.append("Isolation Forest detected anomalies - consider multivariate analysis")
        
        if 'clustering_outlier' in methods_used:
            recommendations.append("Clustering detected outliers - review data collection processes")
        
        # Severity-based recommendations
        high_severity_count = sum(1 for anomaly in detection_results.get('anomalies', []) 
                                if anomaly.get('severity') == 'high')
        if high_severity_count > 0:
            recommendations.append(f"Address {high_severity_count} high-severity anomalies immediately")
        
        return recommendations
    
    async def _learn_from_detection_session(self, detection_results: Dict[str, Any], 
                                          intelligent_analysis: Dict[str, Any]) -> None:
        """Learn from detection session to improve future detections."""
        session_id = f"detection_{datetime.utcnow().timestamp()}"
        
        self.learning_memory[session_id] = {
            "timestamp": datetime.utcnow().isoformat(),
            "detection_results": detection_results,
            "intelligent_analysis": intelligent_analysis,
            "learned_patterns": self._extract_detection_patterns(detection_results)
        }
        
        # Update anomaly models based on learning
        await self._update_anomaly_models_from_learning()
    
    def _extract_detection_patterns(self, detection_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract learning patterns from detection results."""
        patterns = {
            "effective_methods": detection_results.get('methods_used', []),
            "common_anomaly_types": {},
            "severity_distribution": {}
        }
        
        # Analyze anomaly types and severity
        for anomaly in detection_results.get('anomalies', []):
            anomaly_type = anomaly.get('type', 'unknown')
            severity = anomaly.get('severity', 'unknown')
            
            patterns["common_anomaly_types"][anomaly_type] = patterns["common_anomaly_types"].get(anomaly_type, 0) + 1
            patterns["severity_distribution"][severity] = patterns["severity_distribution"].get(severity, 0) + 1
        
        return patterns
    
    async def _update_anomaly_models_from_learning(self) -> None:
        """Update anomaly models based on learning patterns."""
        # Implement model update logic based on learning memory
        pass
