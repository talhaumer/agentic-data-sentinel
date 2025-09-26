"""Learning Agent for continuous improvement and adaptive intelligence."""

from typing import Dict, Any, List, Optional, Tuple
import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from .base_agent import BaseAgent, AgentContext, AgentResult, AgentStatus, Priority
from ..core.config import get_settings
import structlog

logger = structlog.get_logger(__name__)


class LearningType(Enum):
    """Types of learning."""
    ANOMALY_PATTERN = "anomaly_pattern"
    THRESHOLD_ADAPTATION = "threshold_adaptation"
    REMEDIATION_EFFECTIVENESS = "remediation_effectiveness"
    NOTIFICATION_OPTIMIZATION = "notification_optimization"
    BUSINESS_IMPACT = "business_impact"
    USER_FEEDBACK = "user_feedback"


class LearningStatus(Enum):
    """Learning status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATED = "validated"


@dataclass
class LearningInsight:
    """Learning insight result."""
    insight_type: LearningType
    description: str
    confidence: float
    evidence: Dict[str, Any]
    recommendations: List[str]
    impact_score: float
    created_at: datetime
    validated: bool = False
    validation_feedback: Optional[str] = None


@dataclass
class ModelUpdate:
    """Model update information."""
    model_name: str
    update_type: str
    parameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    validation_score: float
    created_at: datetime
    deployed: bool = False


class LearningAgent(BaseAgent):
    """Agent for continuous learning and system improvement."""
    
    def __init__(self):
        super().__init__(
            name="learning_agent",
            description="Tracks past decisions and outcomes to improve future anomaly detection and system performance"
        )
        self.settings = get_settings()
        self.learning_history = []
        self.model_updates = []
        self.performance_metrics = self._initialize_performance_metrics()
        self.learning_models = self._initialize_learning_models()
        self.feedback_system = self._initialize_feedback_system()
    
    def _initialize_performance_metrics(self) -> Dict[str, Any]:
        """Initialize performance tracking metrics."""
        return {
            "anomaly_detection": {
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "false_positive_rate": 0.0,
                "accuracy": 0.0
            },
            "remediation": {
                "success_rate": 0.0,
                "average_resolution_time": 0.0,
                "escalation_rate": 0.0,
                "user_satisfaction": 0.0
            },
            "notifications": {
                "delivery_rate": 0.0,
                "response_rate": 0.0,
                "escalation_rate": 0.0,
                "user_engagement": 0.0
            },
            "business_impact": {
                "cost_savings": 0.0,
                "downtime_reduction": 0.0,
                "data_quality_improvement": 0.0,
                "user_productivity": 0.0
            }
        }
    
    def _initialize_learning_models(self) -> Dict[str, Any]:
        """Initialize learning models."""
        return {
            "anomaly_classifier": {
                "type": "classification",
                "features": ["severity", "confidence", "anomaly_type", "business_impact"],
                "model": None,
                "last_updated": None,
                "performance": {}
            },
            "threshold_optimizer": {
                "type": "regression",
                "features": ["historical_data", "seasonal_patterns", "business_cycles"],
                "model": None,
                "last_updated": None,
                "performance": {}
            },
            "remediation_predictor": {
                "type": "classification",
                "features": ["anomaly_type", "severity", "business_impact", "data_volume"],
                "model": None,
                "last_updated": None,
                "performance": {}
            },
            "notification_optimizer": {
                "type": "recommendation",
                "features": ["user_preferences", "anomaly_type", "severity", "time_of_day"],
                "model": None,
                "last_updated": None,
                "performance": {}
            }
        }
    
    def _initialize_feedback_system(self) -> Dict[str, Any]:
        """Initialize feedback collection system."""
        return {
            "feedback_sources": [
                "user_ratings",
                "resolution_feedback",
                "false_positive_reports",
                "escalation_feedback",
                "business_impact_reports"
            ],
            "feedback_weights": {
                "user_ratings": 0.3,
                "resolution_feedback": 0.25,
                "false_positive_reports": 0.2,
                "escalation_feedback": 0.15,
                "business_impact_reports": 0.1
            },
            "feedback_threshold": 0.7
        }
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if agent can handle the context."""
        return "learning_data" in context.metadata or "feedback" in context.metadata or "performance_data" in context.metadata
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute learning and improvement processes."""
        try:
            # Extract learning data from context
            learning_data = context.metadata.get("learning_data", {})
            feedback_data = context.metadata.get("feedback", {})
            performance_data = context.metadata.get("performance_data", {})
            
            # Process different types of learning
            learning_results = []
            
            # Anomaly pattern learning
            if "anomalies" in learning_data:
                anomaly_insights = await self._learn_anomaly_patterns(learning_data["anomalies"])
                learning_results.extend(anomaly_insights)
            
            # Threshold adaptation learning
            if "threshold_data" in learning_data:
                threshold_insights = await self._learn_threshold_adaptations(learning_data["threshold_data"])
                learning_results.extend(threshold_insights)
            
            # Remediation effectiveness learning
            if "remediation_data" in learning_data:
                remediation_insights = await self._learn_remediation_effectiveness(learning_data["remediation_data"])
                learning_results.extend(remediation_insights)
            
            # Notification optimization learning
            if "notification_data" in learning_data:
                notification_insights = await self._learn_notification_optimization(learning_data["notification_data"])
                learning_results.extend(notification_insights)
            
            # Business impact learning
            if "business_impact_data" in learning_data:
                business_insights = await self._learn_business_impact(learning_data["business_impact_data"])
                learning_results.extend(business_insights)
            
            # Process user feedback
            if feedback_data:
                feedback_insights = await self._process_user_feedback(feedback_data)
                learning_results.extend(feedback_insights)
            
            # Update performance metrics
            if performance_data:
                await self._update_performance_metrics(performance_data)
            
            # Generate model updates
            model_updates = await self._generate_model_updates(learning_results)
            
            # Generate learning report
            learning_report = self._generate_learning_report(learning_results, model_updates)
            
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "learning_insights": [self._insight_to_dict(i) for i in learning_results],
                    "model_updates": [self._model_update_to_dict(m) for m in model_updates],
                    "learning_report": learning_report,
                    "performance_metrics": self.performance_metrics,
                    "total_insights": len(learning_results),
                    "model_updates_count": len(model_updates)
                },
                confidence=0.9,
                recommendations=self._generate_learning_recommendations(learning_results),
                next_actions=self._determine_next_actions(learning_results, model_updates)
            )
            
        except Exception as e:
            logger.error("Learning execution failed", error=str(e))
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                data={},
                error=str(e)
            )
    
    async def _learn_anomaly_patterns(self, anomalies: List[Dict[str, Any]]) -> List[LearningInsight]:
        """Learn patterns from anomaly data."""
        insights = []
        
        try:
            # Analyze anomaly frequency patterns
            anomaly_types = [a.get("anomaly_type", "unknown") for a in anomalies]
            type_counts = pd.Series(anomaly_types).value_counts()
            
            # Identify frequent anomaly types
            frequent_types = type_counts[type_counts > len(anomalies) * 0.1]
            if len(frequent_types) > 0:
                insights.append(LearningInsight(
                    insight_type=LearningType.ANOMALY_PATTERN,
                    description=f"Frequent anomaly types detected: {', '.join(frequent_types.index)}",
                    confidence=0.8,
                    evidence={"type_counts": type_counts.to_dict(), "threshold": 0.1},
                    recommendations=[
                        "Investigate root causes of frequent anomaly types",
                        "Implement preventive measures for common issues",
                        "Update detection rules for better accuracy"
                    ],
                    impact_score=0.7,
                    created_at=datetime.utcnow()
                ))
            
            # Analyze severity patterns
            severities = [a.get("severity", 1) for a in anomalies]
            avg_severity = np.mean(severities)
            high_severity_count = len([s for s in severities if s >= 4])
            
            if high_severity_count > len(anomalies) * 0.2:
                insights.append(LearningInsight(
                    insight_type=LearningType.ANOMALY_PATTERN,
                    description=f"High severity anomaly rate: {high_severity_count/len(anomalies):.1%}",
                    confidence=0.9,
                    evidence={"high_severity_count": high_severity_count, "total_anomalies": len(anomalies)},
                    recommendations=[
                        "Review data quality processes",
                        "Implement stricter validation rules",
                        "Increase monitoring frequency"
                    ],
                    impact_score=0.9,
                    created_at=datetime.utcnow()
                ))
            
            # Analyze temporal patterns
            if len(anomalies) > 10:
                timestamps = [datetime.fromisoformat(a.get("detected_at", datetime.utcnow().isoformat())) for a in anomalies]
                hourly_counts = pd.Series([t.hour for t in timestamps]).value_counts()
                
                peak_hours = hourly_counts[hourly_counts > hourly_counts.mean() * 1.5]
                if len(peak_hours) > 0:
                    insights.append(LearningInsight(
                        insight_type=LearningType.ANOMALY_PATTERN,
                        description=f"Peak anomaly hours: {', '.join(map(str, peak_hours.index))}",
                        confidence=0.7,
                        evidence={"hourly_counts": hourly_counts.to_dict(), "peak_hours": peak_hours.to_dict()},
                        recommendations=[
                            "Increase monitoring during peak hours",
                            "Investigate business processes during peak times",
                            "Adjust resource allocation for peak periods"
                        ],
                        impact_score=0.6,
                        created_at=datetime.utcnow()
                    ))
            
        except Exception as e:
            logger.error("Anomaly pattern learning failed", error=str(e))
        
        return insights
    
    async def _learn_threshold_adaptations(self, threshold_data: Dict[str, Any]) -> List[LearningInsight]:
        """Learn optimal thresholds from historical data."""
        insights = []
        
        try:
            # Analyze threshold performance
            current_thresholds = threshold_data.get("current_thresholds", {})
            performance_metrics = threshold_data.get("performance_metrics", {})
            
            for metric_name, current_threshold in current_thresholds.items():
                if metric_name in performance_metrics:
                    metrics = performance_metrics[metric_name]
                    
                    # Calculate optimal threshold
                    optimal_threshold = self._calculate_optimal_threshold(metrics)
                    
                    if abs(optimal_threshold - current_threshold) > current_threshold * 0.1:
                        insights.append(LearningInsight(
                            insight_type=LearningType.THRESHOLD_ADAPTATION,
                            description=f"Optimal threshold for {metric_name}: {optimal_threshold:.3f} (current: {current_threshold:.3f})",
                            confidence=0.8,
                            evidence={
                                "current_threshold": current_threshold,
                                "optimal_threshold": optimal_threshold,
                                "performance_metrics": metrics
                            },
                            recommendations=[
                                f"Update {metric_name} threshold to {optimal_threshold:.3f}",
                                "Monitor performance after threshold update",
                                "A/B test threshold changes in production"
                            ],
                            impact_score=0.7,
                            created_at=datetime.utcnow()
                        ))
            
        except Exception as e:
            logger.error("Threshold adaptation learning failed", error=str(e))
        
        return insights
    
    def _calculate_optimal_threshold(self, metrics: Dict[str, Any]) -> float:
        """Calculate optimal threshold using ROC curve analysis."""
        # Simplified implementation - would use actual ROC analysis
        precision = metrics.get("precision", 0.8)
        recall = metrics.get("recall", 0.8)
        f1_score = metrics.get("f1_score", 0.8)
        
        # Use F1 score as primary metric
        if f1_score > 0.8:
            return metrics.get("current_threshold", 0.5) * 0.9  # Lower threshold for better recall
        elif f1_score < 0.6:
            return metrics.get("current_threshold", 0.5) * 1.1  # Higher threshold for better precision
        else:
            return metrics.get("current_threshold", 0.5)
    
    async def _learn_remediation_effectiveness(self, remediation_data: List[Dict[str, Any]]) -> List[LearningInsight]:
        """Learn from remediation effectiveness data."""
        insights = []
        
        try:
            # Analyze remediation success rates
            success_rates = {}
            resolution_times = {}
            
            for remediation in remediation_data:
                action = remediation.get("action", "unknown")
                success = remediation.get("success", False)
                resolution_time = remediation.get("resolution_time", 0)
                
                if action not in success_rates:
                    success_rates[action] = {"success": 0, "total": 0}
                    resolution_times[action] = []
                
                success_rates[action]["total"] += 1
                if success:
                    success_rates[action]["success"] += 1
                
                if resolution_time > 0:
                    resolution_times[action].append(resolution_time)
            
            # Identify most effective remediation actions
            for action, rates in success_rates.items():
                if rates["total"] >= 5:  # Minimum sample size
                    success_rate = rates["success"] / rates["total"]
                    avg_resolution_time = np.mean(resolution_times.get(action, [0]))
                    
                    if success_rate > 0.8:
                        insights.append(LearningInsight(
                            insight_type=LearningType.REMEDIATION_EFFECTIVENESS,
                            description=f"Highly effective remediation action: {action} (success rate: {success_rate:.1%})",
                            confidence=0.9,
                            evidence={
                                "action": action,
                                "success_rate": success_rate,
                                "total_attempts": rates["total"],
                                "avg_resolution_time": avg_resolution_time
                            },
                            recommendations=[
                                f"Prioritize {action} for similar anomalies",
                                "Document best practices for {action}",
                                "Train team on effective {action} techniques"
                            ],
                            impact_score=0.8,
                            created_at=datetime.utcnow()
                        ))
                    
                    elif success_rate < 0.5:
                        insights.append(LearningInsight(
                            insight_type=LearningType.REMEDIATION_EFFECTIVENESS,
                            description=f"Ineffective remediation action: {action} (success rate: {success_rate:.1%})",
                            confidence=0.8,
                            evidence={
                                "action": action,
                                "success_rate": success_rate,
                                "total_attempts": rates["total"],
                                "avg_resolution_time": avg_resolution_time
                            },
                            recommendations=[
                                f"Review and improve {action} process",
                                "Consider alternative remediation approaches",
                                "Investigate root causes of {action} failures"
                            ],
                            impact_score=0.6,
                            created_at=datetime.utcnow()
                        ))
            
        except Exception as e:
            logger.error("Remediation effectiveness learning failed", error=str(e))
        
        return insights
    
    async def _learn_notification_optimization(self, notification_data: List[Dict[str, Any]]) -> List[LearningInsight]:
        """Learn from notification effectiveness data."""
        insights = []
        
        try:
            # Analyze notification delivery and response rates
            channel_performance = {}
            
            for notification in notification_data:
                channel = notification.get("channel", "unknown")
                delivered = notification.get("delivered", False)
                responded = notification.get("responded", False)
                response_time = notification.get("response_time", 0)
                
                if channel not in channel_performance:
                    channel_performance[channel] = {
                        "delivered": 0,
                        "total": 0,
                        "responded": 0,
                        "response_times": []
                    }
                
                channel_performance[channel]["total"] += 1
                if delivered:
                    channel_performance[channel]["delivered"] += 1
                if responded:
                    channel_performance[channel]["responded"] += 1
                if response_time > 0:
                    channel_performance[channel]["response_times"].append(response_time)
            
            # Identify best performing channels
            for channel, perf in channel_performance.items():
                if perf["total"] >= 10:  # Minimum sample size
                    delivery_rate = perf["delivered"] / perf["total"]
                    response_rate = perf["responded"] / perf["delivered"] if perf["delivered"] > 0 else 0
                    avg_response_time = np.mean(perf["response_times"]) if perf["response_times"] else 0
                    
                    if delivery_rate > 0.9 and response_rate > 0.7:
                        insights.append(LearningInsight(
                            insight_type=LearningType.NOTIFICATION_OPTIMIZATION,
                            description=f"High-performing notification channel: {channel} (delivery: {delivery_rate:.1%}, response: {response_rate:.1%})",
                            confidence=0.9,
                            evidence={
                                "channel": channel,
                                "delivery_rate": delivery_rate,
                                "response_rate": response_rate,
                                "avg_response_time": avg_response_time
                            },
                            recommendations=[
                                f"Prioritize {channel} for critical notifications",
                                f"Use {channel} as primary channel for urgent alerts",
                                "Replicate {channel} success patterns for other channels"
                            ],
                            impact_score=0.8,
                            created_at=datetime.utcnow()
                        ))
                    
                    elif delivery_rate < 0.8 or response_rate < 0.5:
                        insights.append(LearningInsight(
                            insight_type=LearningType.NOTIFICATION_OPTIMIZATION,
                            description=f"Underperforming notification channel: {channel} (delivery: {delivery_rate:.1%}, response: {response_rate:.1%})",
                            confidence=0.8,
                            evidence={
                                "channel": channel,
                                "delivery_rate": delivery_rate,
                                "response_rate": response_rate,
                                "avg_response_time": avg_response_time
                            },
                            recommendations=[
                                f"Investigate {channel} delivery issues",
                                f"Improve {channel} message formatting",
                                f"Consider alternative channels for {channel} use cases"
                            ],
                            impact_score=0.6,
                            created_at=datetime.utcnow()
                        ))
            
        except Exception as e:
            logger.error("Notification optimization learning failed", error=str(e))
        
        return insights
    
    async def _learn_business_impact(self, business_data: Dict[str, Any]) -> List[LearningInsight]:
        """Learn from business impact data."""
        insights = []
        
        try:
            # Analyze cost savings and productivity improvements
            cost_savings = business_data.get("cost_savings", 0)
            downtime_reduction = business_data.get("downtime_reduction", 0)
            data_quality_improvement = business_data.get("data_quality_improvement", 0)
            
            if cost_savings > 0:
                insights.append(LearningInsight(
                    insight_type=LearningType.BUSINESS_IMPACT,
                    description=f"Significant cost savings achieved: ${cost_savings:,.2f}",
                    confidence=0.9,
                    evidence={"cost_savings": cost_savings},
                    recommendations=[
                        "Document cost-saving strategies for replication",
                        "Scale successful cost-saving initiatives",
                        "Report ROI to stakeholders"
                    ],
                    impact_score=0.9,
                    created_at=datetime.utcnow()
                ))
            
            if downtime_reduction > 0:
                insights.append(LearningInsight(
                    insight_type=LearningType.BUSINESS_IMPACT,
                    description=f"Downtime reduced by {downtime_reduction:.1f} hours",
                    confidence=0.8,
                    evidence={"downtime_reduction": downtime_reduction},
                    recommendations=[
                        "Implement proactive monitoring to prevent downtime",
                        "Scale downtime reduction strategies",
                        "Measure and report availability improvements"
                    ],
                    impact_score=0.8,
                    created_at=datetime.utcnow()
                ))
            
            if data_quality_improvement > 0:
                insights.append(LearningInsight(
                    insight_type=LearningType.BUSINESS_IMPACT,
                    description=f"Data quality improved by {data_quality_improvement:.1%}",
                    confidence=0.8,
                    evidence={"data_quality_improvement": data_quality_improvement},
                    recommendations=[
                        "Continue data quality improvement initiatives",
                        "Share data quality best practices",
                        "Set higher data quality targets"
                    ],
                    impact_score=0.7,
                    created_at=datetime.utcnow()
                ))
            
        except Exception as e:
            logger.error("Business impact learning failed", error=str(e))
        
        return insights
    
    async def _process_user_feedback(self, feedback_data: Dict[str, Any]) -> List[LearningInsight]:
        """Process user feedback for learning."""
        insights = []
        
        try:
            feedback_type = feedback_data.get("type", "general")
            rating = feedback_data.get("rating", 0)
            comments = feedback_data.get("comments", "")
            
            if rating >= 4:
                insights.append(LearningInsight(
                    insight_type=LearningType.USER_FEEDBACK,
                    description=f"Positive user feedback received (rating: {rating}/5)",
                    confidence=0.9,
                    evidence={"rating": rating, "comments": comments},
                    recommendations=[
                        "Continue current practices",
                        "Share positive feedback with team",
                        "Identify and replicate successful patterns"
                    ],
                    impact_score=0.8,
                    created_at=datetime.utcnow()
                ))
            elif rating <= 2:
                insights.append(LearningInsight(
                    insight_type=LearningType.USER_FEEDBACK,
                    description=f"Negative user feedback received (rating: {rating}/5)",
                    confidence=0.8,
                    evidence={"rating": rating, "comments": comments},
                    recommendations=[
                        "Investigate feedback concerns",
                        "Implement improvements based on feedback",
                        "Follow up with user for additional details"
                    ],
                    impact_score=0.7,
                    created_at=datetime.utcnow()
                ))
            
        except Exception as e:
            logger.error("User feedback processing failed", error=str(e))
        
        return insights
    
    async def _update_performance_metrics(self, performance_data: Dict[str, Any]) -> None:
        """Update performance metrics with new data."""
        try:
            for category, metrics in performance_data.items():
                if category in self.performance_metrics:
                    for metric_name, value in metrics.items():
                        if metric_name in self.performance_metrics[category]:
                            # Use exponential moving average for smooth updates
                            alpha = 0.1  # Learning rate
                            current_value = self.performance_metrics[category][metric_name]
                            self.performance_metrics[category][metric_name] = alpha * value + (1 - alpha) * current_value
            
        except Exception as e:
            logger.error("Performance metrics update failed", error=str(e))
    
    async def _generate_model_updates(self, insights: List[LearningInsight]) -> List[ModelUpdate]:
        """Generate model updates based on learning insights."""
        model_updates = []
        
        try:
            # Generate updates for each learning model
            for model_name, model_info in self.learning_models.items():
                if model_info["last_updated"] is None or \
                   (datetime.utcnow() - model_info["last_updated"]).days > 7:
                    
                    # Determine if model needs update based on insights
                    relevant_insights = [i for i in insights if self._is_insight_relevant_to_model(i, model_name)]
                    
                    if relevant_insights:
                        update = await self._create_model_update(model_name, relevant_insights)
                        model_updates.append(update)
            
        except Exception as e:
            logger.error("Model update generation failed", error=str(e))
        
        return model_updates
    
    def _is_insight_relevant_to_model(self, insight: LearningInsight, model_name: str) -> bool:
        """Check if insight is relevant to a specific model."""
        relevance_map = {
            "anomaly_classifier": [LearningType.ANOMALY_PATTERN, LearningType.USER_FEEDBACK],
            "threshold_optimizer": [LearningType.THRESHOLD_ADAPTATION, LearningType.ANOMALY_PATTERN],
            "remediation_predictor": [LearningType.REMEDIATION_EFFECTIVENESS, LearningType.USER_FEEDBACK],
            "notification_optimizer": [LearningType.NOTIFICATION_OPTIMIZATION, LearningType.USER_FEEDBACK]
        }
        
        return insight.insight_type in relevance_map.get(model_name, [])
    
    async def _create_model_update(self, model_name: str, insights: List[LearningInsight]) -> ModelUpdate:
        """Create a model update based on insights."""
        # Simplified implementation - would use actual ML model training
        update_type = "incremental" if len(insights) < 5 else "full_retrain"
        
        # Calculate performance metrics based on insights
        confidence_scores = [i.confidence for i in insights]
        impact_scores = [i.impact_score for i in insights]
        
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.5
        avg_impact = np.mean(impact_scores) if impact_scores else 0.5
        
        return ModelUpdate(
            model_name=model_name,
            update_type=update_type,
            parameters={
                "learning_rate": 0.001,
                "batch_size": 32,
                "epochs": 10,
                "validation_split": 0.2
            },
            performance_metrics={
                "accuracy": avg_confidence,
                "precision": avg_confidence * 0.9,
                "recall": avg_confidence * 0.85,
                "f1_score": avg_confidence * 0.87
            },
            validation_score=avg_confidence * avg_impact,
            created_at=datetime.utcnow()
        )
    
    def _generate_learning_report(self, insights: List[LearningInsight], model_updates: List[ModelUpdate]) -> Dict[str, Any]:
        """Generate comprehensive learning report."""
        return {
            "summary": {
                "total_insights": len(insights),
                "model_updates": len(model_updates),
                "learning_timestamp": datetime.utcnow().isoformat()
            },
            "insight_categories": {
                insight_type.value: len([i for i in insights if i.insight_type == insight_type])
                for insight_type in LearningType
            },
            "confidence_distribution": {
                "high": len([i for i in insights if i.confidence >= 0.8]),
                "medium": len([i for i in insights if 0.6 <= i.confidence < 0.8]),
                "low": len([i for i in insights if i.confidence < 0.6])
            },
            "impact_distribution": {
                "high": len([i for i in insights if i.impact_score >= 0.8]),
                "medium": len([i for i in insights if 0.6 <= i.impact_score < 0.8]),
                "low": len([i for i in insights if i.impact_score < 0.6])
            },
            "model_update_summary": {
                "total_updates": len(model_updates),
                "update_types": {
                    "incremental": len([m for m in model_updates if m.update_type == "incremental"]),
                    "full_retrain": len([m for m in model_updates if m.update_type == "full_retrain"])
                }
            },
            "performance_metrics": self.performance_metrics
        }
    
    def _generate_learning_recommendations(self, insights: List[LearningInsight]) -> List[str]:
        """Generate learning recommendations."""
        recommendations = []
        
        if not insights:
            recommendations.append("📊 No new learning insights - continue monitoring")
            return recommendations
        
        # High confidence insights
        high_confidence_insights = [i for i in insights if i.confidence >= 0.8]
        if high_confidence_insights:
            recommendations.append(f"🎯 {len(high_confidence_insights)} high-confidence insights - prioritize implementation")
        
        # High impact insights
        high_impact_insights = [i for i in insights if i.impact_score >= 0.8]
        if high_impact_insights:
            recommendations.append(f"💡 {len(high_impact_insights)} high-impact insights - focus on business value")
        
        # Pattern-based recommendations
        anomaly_pattern_insights = [i for i in insights if i.insight_type == LearningType.ANOMALY_PATTERN]
        if anomaly_pattern_insights:
            recommendations.append("🔍 Anomaly patterns detected - update detection rules")
        
        threshold_insights = [i for i in insights if i.insight_type == LearningType.THRESHOLD_ADAPTATION]
        if threshold_insights:
            recommendations.append("⚙️ Threshold optimizations available - update configuration")
        
        remediation_insights = [i for i in insights if i.insight_type == LearningType.REMEDIATION_EFFECTIVENESS]
        if remediation_insights:
            recommendations.append("🔧 Remediation effectiveness insights - improve processes")
        
        # General recommendations
        recommendations.extend([
            "📈 Monitor learning progress and model performance",
            "🔄 Implement continuous learning feedback loop",
            "📚 Document learning insights for knowledge sharing"
        ])
        
        return recommendations
    
    def _determine_next_actions(self, insights: List[LearningInsight], model_updates: List[ModelUpdate]) -> List[str]:
        """Determine next actions based on learning results."""
        actions = []
        
        if insights:
            actions.append("update_learning_database")
            actions.append("implement_high_confidence_insights")
        
        if model_updates:
            actions.append("deploy_model_updates")
            actions.append("validate_model_performance")
        
        actions.extend([
            "schedule_next_learning_cycle",
            "update_system_configuration",
            "notify_team_of_improvements"
        ])
        
        return actions
    
    def _insight_to_dict(self, insight: LearningInsight) -> Dict[str, Any]:
        """Convert learning insight to dictionary."""
        return {
            "insight_type": insight.insight_type.value,
            "description": insight.description,
            "confidence": insight.confidence,
            "evidence": insight.evidence,
            "recommendations": insight.recommendations,
            "impact_score": insight.impact_score,
            "created_at": insight.created_at.isoformat(),
            "validated": insight.validated,
            "validation_feedback": insight.validation_feedback
        }
    
    def _model_update_to_dict(self, model_update: ModelUpdate) -> Dict[str, Any]:
        """Convert model update to dictionary."""
        return {
            "model_name": model_update.model_name,
            "update_type": model_update.update_type,
            "parameters": model_update.parameters,
            "performance_metrics": model_update.performance_metrics,
            "validation_score": model_update.validation_score,
            "created_at": model_update.created_at.isoformat(),
            "deployed": model_update.deployed
        }
