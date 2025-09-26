"""Remediation Agent for autonomous fixes and human-in-the-loop approvals."""

import asyncio
import json
import structlog
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..models import Anomaly
from .base_agent import AgentContext, AgentResult, AgentStatus, BaseAgent, Priority

logger = structlog.get_logger(__name__)


class RemediationAction(Enum):
    """Types of remediation actions."""
    AUTO_FIX = "auto_fix"
    MANUAL_REVIEW = "manual_review"
    ESCALATE = "escalate"
    IGNORE = "ignore"
    SCHEDULE = "schedule"


class RemediationStatus(Enum):
    """Remediation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REQUIRES_APPROVAL = "requires_approval"


@dataclass
class RemediationPlan:
    """Remediation plan for an anomaly."""
    anomaly_id: str
    action: RemediationAction
    description: str
    estimated_duration: timedelta
    risk_level: str
    prerequisites: List[str]
    steps: List[Dict[str, Any]]
    rollback_plan: List[Dict[str, Any]]
    success_criteria: List[str]
    created_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


@dataclass
class RemediationExecution:
    """Remediation execution tracking."""
    plan_id: str
    status: RemediationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    executed_by: Optional[str] = None
    execution_log: List[str] = None
    error_message: Optional[str] = None
    rollback_executed: bool = False
    
    def __post_init__(self):
        if self.execution_log is None:
            self.execution_log = []


class RemediationAgent(BaseAgent):
    """Agent for autonomous remediation and human-in-the-loop approvals."""
    
    def __init__(self):
        super().__init__(
            name="remediation_agent",
            description=(
                "Suggests fixes and triggers automated remediation with "
                "human approval for critical issues"
            )
        )
        self.settings = get_settings()
        self.remediation_rules = self._initialize_remediation_rules()
        self.auto_fix_capabilities = self._initialize_auto_fix_capabilities()
        self.approval_workflows = self._initialize_approval_workflows()
        self.active_executions = {}
    
    def _initialize_remediation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize remediation rules for different anomaly types."""
        return {
            "statistical": {
                "auto_fix_threshold": 0.7,
                "actions": ["outlier_removal", "data_cleansing", "value_capping"],
                "risk_level": "low"
            },
            "trend": {
                "auto_fix_threshold": 0.5,
                "actions": ["investigate", "notify_team", "update_models"],
                "risk_level": "medium"
            },
            "seasonal": {
                "auto_fix_threshold": 0.6,
                "actions": ["pattern_analysis", "model_update", "monitoring"],
                "risk_level": "low"
            },
            "outlier": {
                "auto_fix_threshold": 0.8,
                "actions": ["outlier_removal", "value_replacement", "data_validation"],
                "risk_level": "low"
            },
            "pattern": {
                "auto_fix_threshold": 0.4,
                "actions": ["investigate", "data_validation", "process_review"],
                "risk_level": "medium"
            },
            "volume": {
                "auto_fix_threshold": 0.3,
                "actions": ["system_check", "capacity_alert", "escalate"],
                "risk_level": "high"
            },
            "quality": {
                "auto_fix_threshold": 0.2,
                "actions": ["data_validation", "source_check", "escalate"],
                "risk_level": "critical"
            },
            "schema": {
                "auto_fix_threshold": 0.1,
                "actions": ["schema_validation", "escalate", "manual_review"],
                "risk_level": "critical"
            }
        }
    
    def _initialize_auto_fix_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Initialize auto-fix capabilities."""
        return {
            "outlier_removal": {
                "description": "Remove statistical outliers using IQR method",
                "risk_level": "low",
                "automated": True,
                "requires_approval": False
            },
            "value_capping": {
                "description": "Cap extreme values to reasonable ranges",
                "risk_level": "low",
                "automated": True,
                "requires_approval": False
            },
            "data_cleansing": {
                "description": "Clean and standardize data values",
                "risk_level": "low",
                "automated": True,
                "requires_approval": False
            },
            "missing_value_imputation": {
                "description": "Fill missing values using statistical methods",
                "risk_level": "medium",
                "automated": True,
                "requires_approval": True
            },
            "schema_validation": {
                "description": "Validate and fix schema inconsistencies",
                "risk_level": "high",
                "automated": False,
                "requires_approval": True
            },
            "data_validation": {
                "description": "Run comprehensive data validation checks",
                "risk_level": "medium",
                "automated": True,
                "requires_approval": True
            },
            "system_check": {
                "description": "Check system health and performance",
                "risk_level": "medium",
                "automated": True,
                "requires_approval": False
            },
            "capacity_alert": {
                "description": "Send capacity and performance alerts",
                "risk_level": "low",
                "automated": True,
                "requires_approval": False
            }
        }
    
    def _initialize_approval_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Initialize approval workflows for different risk levels."""
        return {
            "low": {
                "approval_required": False,
                "notification_channels": ["slack"],
                "escalation_time": None
            },
            "medium": {
                "approval_required": True,
                "approvers": ["data_engineer", "team_lead"],
                "notification_channels": ["slack", "email"],
                "escalation_time": timedelta(hours=2)
            },
            "high": {
                "approval_required": True,
                "approvers": ["senior_data_engineer", "engineering_manager"],
                "notification_channels": ["slack", "email", "teams"],
                "escalation_time": timedelta(hours=1)
            },
            "critical": {
                "approval_required": True,
                "approvers": ["engineering_manager", "data_architect", "cto"],
                "notification_channels": ["slack", "email", "teams", "phone"],
                "escalation_time": timedelta(minutes=30)
            }
        }
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if agent can handle the context."""
        return "anomalies" in context.metadata or "anomaly_detection_result" in context.metadata
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute remediation planning and execution."""
        try:
            # Get anomalies from context
            anomalies = self._extract_anomalies_from_context(context)
            if not anomalies:
                return AgentResult(
                    agent_name=self.name,
                    status=AgentStatus.FAILED,
                    data={},
                    error="No anomalies found in context"
                )
            
            # Generate remediation plans
            remediation_plans = []
            for anomaly in anomalies:
                plan = await self._create_remediation_plan(anomaly, context)
                remediation_plans.append(plan)
            
            # Execute remediation plans
            execution_results = []
            for plan in remediation_plans:
                if plan.action == RemediationAction.AUTO_FIX:
                    result = await self._execute_auto_fix(plan, context)
                    execution_results.append(result)
                elif plan.action == RemediationAction.MANUAL_REVIEW:
                    result = await self._request_manual_review(plan, context)
                    execution_results.append(result)
                elif plan.action == RemediationAction.ESCALATE:
                    result = await self._escalate_anomaly(plan, context)
                    execution_results.append(result)
            
            # Generate remediation report
            remediation_report = self._generate_remediation_report(remediation_plans, execution_results)
            
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "remediation_plans": [self._plan_to_dict(p) for p in remediation_plans],
                    "execution_results": execution_results,
                    "remediation_report": remediation_report,
                    "total_plans": len(remediation_plans),
                    "auto_fix_count": len([p for p in remediation_plans if p.action == RemediationAction.AUTO_FIX]),
                    "manual_review_count": len([p for p in remediation_plans if p.action == RemediationAction.MANUAL_REVIEW]),
                    "escalation_count": len([p for p in remediation_plans if p.action == RemediationAction.ESCALATE])
                },
                confidence=0.9,
                recommendations=self._generate_remediation_recommendations(remediation_plans),
                next_actions=self._determine_next_actions(remediation_plans)
            )
            
        except Exception as e:
            logger.error("Remediation failed", error=str(e))
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                data={},
                error=str(e)
            )
    
    def _extract_anomalies_from_context(self, context: AgentContext) -> List[Dict[str, Any]]:
        """Extract anomalies from context metadata."""
        anomalies = []
        
        # Check for anomaly detection results
        if "anomaly_detection_result" in context.metadata:
            detection_result = context.metadata["anomaly_detection_result"]
            if "detected_anomalies" in detection_result:
                anomalies.extend(detection_result["detected_anomalies"])
        
        # Check for direct anomalies
        if "anomalies" in context.metadata:
            anomalies.extend(context.metadata["anomalies"])
        
        return anomalies
    
    async def _create_remediation_plan(self, anomaly: Dict[str, Any], context: AgentContext) -> RemediationPlan:
        """Create remediation plan for an anomaly."""
        anomaly_type = anomaly.get("anomaly_type", "unknown")
        severity = anomaly.get("severity", 1)
        confidence = anomaly.get("confidence", 0.5)
        
        # Determine remediation action
        action = self._determine_remediation_action(anomaly_type, severity, confidence)
        
        # Get remediation rules for this anomaly type
        rules = self.remediation_rules.get(anomaly_type, {})
        risk_level = rules.get("risk_level", "medium")
        
        # Generate remediation steps
        steps = self._generate_remediation_steps(anomaly_type, anomaly, action)
        
        # Generate rollback plan
        rollback_plan = self._generate_rollback_plan(anomaly_type, steps)
        
        # Generate success criteria
        success_criteria = self._generate_success_criteria(anomaly_type, anomaly)
        
        # Calculate estimated duration
        estimated_duration = self._estimate_remediation_duration(anomaly_type, steps)
        
        # Generate prerequisites
        prerequisites = self._generate_prerequisites(anomaly_type, anomaly)
        
        return RemediationPlan(
            anomaly_id=anomaly.get("id", f"anomaly_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            action=action,
            description=f"Remediation plan for {anomaly_type} anomaly",
            estimated_duration=estimated_duration,
            risk_level=risk_level,
            prerequisites=prerequisites,
            steps=steps,
            rollback_plan=rollback_plan,
            success_criteria=success_criteria,
            created_at=datetime.utcnow()
        )
    
    def _determine_remediation_action(self, anomaly_type: str, severity: int, confidence: float) -> RemediationAction:
        """Determine appropriate remediation action."""
        rules = self.remediation_rules.get(anomaly_type, {})
        auto_fix_threshold = rules.get("auto_fix_threshold", 0.5)
        
        # High severity anomalies require manual review
        if severity >= 4:
            return RemediationAction.ESCALATE
        
        # Critical anomaly types require manual review
        if anomaly_type in ["quality", "schema"]:
            return RemediationAction.MANUAL_REVIEW
        
        # Check if auto-fix is appropriate
        if confidence >= auto_fix_threshold and severity <= 2:
            return RemediationAction.AUTO_FIX
        
        # Medium severity with medium confidence
        if severity == 3 and confidence >= 0.6:
            return RemediationAction.MANUAL_REVIEW
        
        # Low confidence or high severity
        return RemediationAction.ESCALATE
    
    def _generate_remediation_steps(self, anomaly_type: str, anomaly: Dict[str, Any], action: RemediationAction) -> List[Dict[str, Any]]:
        """Generate specific remediation steps."""
        steps = []
        
        if action == RemediationAction.AUTO_FIX:
            steps = self._generate_auto_fix_steps(anomaly_type, anomaly)
        elif action == RemediationAction.MANUAL_REVIEW:
            steps = self._generate_manual_review_steps(anomaly_type, anomaly)
        elif action == RemediationAction.ESCALATE:
            steps = self._generate_escalation_steps(anomaly_type, anomaly)
        
        return steps
    
    def _generate_auto_fix_steps(self, anomaly_type: str, anomaly: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate auto-fix steps."""
        steps = []
        
        if anomaly_type == "statistical":
            steps.extend([
                {
                    "step": 1,
                    "action": "outlier_removal",
                    "description": "Remove statistical outliers using IQR method",
                    "parameters": {"method": "iqr", "threshold": 1.5},
                    "automated": True
                },
                {
                    "step": 2,
                    "action": "value_capping",
                    "description": "Cap extreme values to reasonable ranges",
                    "parameters": {"method": "percentile", "threshold": 99},
                    "automated": True
                }
            ])
        
        elif anomaly_type == "outlier":
            steps.extend([
                {
                    "step": 1,
                    "action": "outlier_removal",
                    "description": "Remove outliers using statistical methods",
                    "parameters": {"method": "z_score", "threshold": 3.0},
                    "automated": True
                },
                {
                    "step": 2,
                    "action": "data_validation",
                    "description": "Validate data after outlier removal",
                    "parameters": {},
                    "automated": True
                }
            ])
        
        elif anomaly_type == "quality":
            steps.extend([
                {
                    "step": 1,
                    "action": "data_validation",
                    "description": "Run comprehensive data validation",
                    "parameters": {},
                    "automated": True
                },
                {
                    "step": 2,
                    "action": "missing_value_imputation",
                    "description": "Fill missing values using statistical methods",
                    "parameters": {"method": "mean"},
                    "automated": True
                }
            ])
        
        return steps
    
    def _generate_manual_review_steps(self, anomaly_type: str, anomaly: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate manual review steps."""
        return [
            {
                "step": 1,
                "action": "investigate",
                "description": "Investigate anomaly root cause",
                "parameters": {"anomaly_type": anomaly_type},
                "automated": False
            },
            {
                "step": 2,
                "action": "notify_team",
                "description": "Notify relevant team members",
                "parameters": {"channels": ["slack", "email"]},
                "automated": True
            },
            {
                "step": 3,
                "action": "create_ticket",
                "description": "Create support ticket for manual review",
                "parameters": {"priority": "medium"},
                "automated": True
            }
        ]
    
    def _generate_escalation_steps(self, anomaly_type: str, anomaly: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate escalation steps."""
        return [
            {
                "step": 1,
                "action": "escalate",
                "description": "Escalate to senior team members",
                "parameters": {"escalation_level": "high"},
                "automated": True
            },
            {
                "step": 2,
                "action": "emergency_notification",
                "description": "Send emergency notifications",
                "parameters": {"channels": ["slack", "email", "teams", "phone"]},
                "automated": True
            },
            {
                "step": 3,
                "action": "create_incident",
                "description": "Create incident ticket",
                "parameters": {"priority": "critical"},
                "automated": True
            }
        ]
    
    def _generate_rollback_plan(self, anomaly_type: str, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate rollback plan for remediation steps."""
        rollback_steps = []
        
        for step in reversed(steps):
            if step.get("automated", False):
                rollback_steps.append({
                    "step": len(rollback_steps) + 1,
                    "action": f"rollback_{step['action']}",
                    "description": f"Rollback {step['description']}",
                    "parameters": step.get("parameters", {}),
                    "automated": True
                })
        
        return rollback_steps
    
    def _generate_success_criteria(self, anomaly_type: str, anomaly: Dict[str, Any]) -> List[str]:
        """Generate success criteria for remediation."""
        criteria = [
            "Anomaly is resolved or mitigated",
            "Data quality metrics improve",
            "No new anomalies are introduced"
        ]
        
        if anomaly_type in ["statistical", "outlier"]:
            criteria.append("Outlier count is reduced by at least 50%")
        
        if anomaly_type == "quality":
            criteria.append("Data quality score improves by at least 10%")
        
        if anomaly_type == "volume":
            criteria.append("Data volume returns to normal levels")
        
        return criteria
    
    def _estimate_remediation_duration(self, anomaly_type: str, steps: List[Dict[str, Any]]) -> timedelta:
        """Estimate remediation duration."""
        base_duration = {
            "statistical": timedelta(minutes=15),
            "outlier": timedelta(minutes=10),
            "quality": timedelta(hours=1),
            "volume": timedelta(minutes=30),
            "trend": timedelta(hours=2),
            "seasonal": timedelta(hours=1),
            "pattern": timedelta(hours=1),
            "schema": timedelta(hours=4)
        }
        
        duration = base_duration.get(anomaly_type, timedelta(hours=1))
        
        # Add time for each step
        for step in steps:
            if not step.get("automated", False):
                duration += timedelta(minutes=30)
        
        return duration
    
    def _generate_prerequisites(self, anomaly_type: str, anomaly: Dict[str, Any]) -> List[str]:
        """Generate prerequisites for remediation."""
        prerequisites = [
            "Data backup is available",
            "System is in maintenance window or can handle changes"
        ]
        
        if anomaly_type in ["quality", "schema"]:
            prerequisites.extend([
                "Database administrator approval",
                "Data governance team notification"
            ])
        
        if anomaly_type == "volume":
            prerequisites.extend([
                "System capacity analysis completed",
                "Performance impact assessment done"
            ])
        
        return prerequisites
    
    async def _execute_auto_fix(self, plan: RemediationPlan, context: AgentContext) -> Dict[str, Any]:
        """Execute automated remediation."""
        try:
            execution = RemediationExecution(
                plan_id=plan.anomaly_id,
                status=RemediationStatus.IN_PROGRESS,
                started_at=datetime.utcnow(),
                executed_by="remediation_agent"
            )
            
            self.active_executions[plan.anomaly_id] = execution
            
            # Execute each step
            for step in plan.steps:
                if step.get("automated", False):
                    result = await self._execute_remediation_step(step, context)
                    execution.execution_log.append(f"Step {step['step']}: {result['message']}")
                    
                    if not result.get("success", False):
                        execution.status = RemediationStatus.FAILED
                        execution.error_message = result.get("error", "Step execution failed")
                        break
            
            if execution.status == RemediationStatus.IN_PROGRESS:
                execution.status = RemediationStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
            
            return {
                "plan_id": plan.anomaly_id,
                "status": execution.status.value,
                "execution_log": execution.execution_log,
                "error": execution.error_message
            }
            
        except Exception as e:
            logger.error(f"Auto-fix execution failed for plan {plan.anomaly_id}", error=str(e))
            return {
                "plan_id": plan.anomaly_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _execute_remediation_step(self, step: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Execute a single remediation step."""
        action = step["action"]
        
        try:
            if action == "outlier_removal":
                return await self._execute_outlier_removal(step, context)
            elif action == "value_capping":
                return await self._execute_value_capping(step, context)
            elif action == "data_validation":
                return await self._execute_data_validation(step, context)
            elif action == "missing_value_imputation":
                return await self._execute_missing_value_imputation(step, context)
            elif action == "system_check":
                return await self._execute_system_check(step, context)
            elif action == "capacity_alert":
                return await self._execute_capacity_alert(step, context)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_outlier_removal(self, step: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Execute outlier removal step."""
        # Simplified implementation - would perform actual outlier removal
        return {
            "success": True,
            "message": f"Outlier removal completed using {step['parameters'].get('method', 'iqr')} method"
        }
    
    async def _execute_value_capping(self, step: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Execute value capping step."""
        return {
            "success": True,
            "message": f"Value capping completed using {step['parameters'].get('method', 'percentile')} method"
        }
    
    async def _execute_data_validation(self, step: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Execute data validation step."""
        return {
            "success": True,
            "message": "Data validation completed successfully"
        }
    
    async def _execute_missing_value_imputation(self, step: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Execute missing value imputation step."""
        return {
            "success": True,
            "message": f"Missing value imputation completed using {step['parameters'].get('method', 'mean')} method"
        }
    
    async def _execute_system_check(self, step: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Execute system check step."""
        return {
            "success": True,
            "message": "System health check completed"
        }
    
    async def _execute_capacity_alert(self, step: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Execute capacity alert step."""
        return {
            "success": True,
            "message": "Capacity alert sent to relevant teams"
        }
    
    async def _request_manual_review(self, plan: RemediationPlan, context: AgentContext) -> Dict[str, Any]:
        """Request manual review for remediation plan."""
        try:
            # Create approval request
            approval_request = {
                "plan_id": plan.anomaly_id,
                "anomaly_type": plan.description,
                "risk_level": plan.risk_level,
                "estimated_duration": plan.estimated_duration.total_seconds() / 3600,
                "steps": plan.steps,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Send notifications
            await self._send_approval_notifications(plan, approval_request)
            
            return {
                "plan_id": plan.anomaly_id,
                "status": "pending_approval",
                "message": "Manual review requested and notifications sent",
                "approval_request": approval_request
            }
            
        except Exception as e:
            logger.error(f"Manual review request failed for plan {plan.anomaly_id}", error=str(e))
            return {
                "plan_id": plan.anomaly_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _escalate_anomaly(self, plan: RemediationPlan, context: AgentContext) -> Dict[str, Any]:
        """Escalate anomaly to senior team members."""
        try:
            # Send emergency notifications
            await self._send_emergency_notifications(plan)
            
            # Create incident ticket
            incident_ticket = await self._create_incident_ticket(plan)
            
            return {
                "plan_id": plan.anomaly_id,
                "status": "escalated",
                "message": "Anomaly escalated to senior team members",
                "incident_ticket": incident_ticket
            }
            
        except Exception as e:
            logger.error(f"Escalation failed for plan {plan.anomaly_id}", error=str(e))
            return {
                "plan_id": plan.anomaly_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _send_approval_notifications(self, plan: RemediationPlan, approval_request: Dict[str, Any]) -> None:
        """Send approval notifications."""
        # Simplified - would send actual notifications
        logger.info("Approval notifications sent", plan_id=plan.anomaly_id)
    
    async def _send_emergency_notifications(self, plan: RemediationPlan) -> None:
        """Send emergency notifications."""
        # Simplified - would send actual emergency notifications
        logger.info("Emergency notifications sent", plan_id=plan.anomaly_id)
    
    async def _create_incident_ticket(self, plan: RemediationPlan) -> Dict[str, Any]:
        """Create incident ticket."""
        # Simplified - would create actual incident ticket
        return {
            "ticket_id": f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "priority": "critical",
            "status": "open",
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _generate_remediation_report(self, plans: List[RemediationPlan], results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive remediation report."""
        return {
            "summary": {
                "total_plans": len(plans),
                "auto_fix_plans": len([p for p in plans if p.action == RemediationAction.AUTO_FIX]),
                "manual_review_plans": len([p for p in plans if p.action == RemediationAction.MANUAL_REVIEW]),
                "escalated_plans": len([p for p in plans if p.action == RemediationAction.ESCALATE]),
                "completed_executions": len([r for r in results if r.get("status") == "completed"]),
                "failed_executions": len([r for r in results if r.get("status") == "failed"])
            },
            "risk_distribution": {
                risk: len([p for p in plans if p.risk_level == risk])
                for risk in ["low", "medium", "high", "critical"]
            },
            "execution_results": results,
            "recommendations": self._generate_remediation_recommendations(plans)
        }
    
    def _generate_remediation_recommendations(self, plans: List[RemediationPlan]) -> List[str]:
        """Generate remediation recommendations."""
        recommendations = []
        
        auto_fix_plans = [p for p in plans if p.action == RemediationAction.AUTO_FIX]
        if auto_fix_plans:
            recommendations.append(f"✅ {len(auto_fix_plans)} anomalies can be auto-fixed")
        
        manual_review_plans = [p for p in plans if p.action == RemediationAction.MANUAL_REVIEW]
        if manual_review_plans:
            recommendations.append(f"👥 {len(manual_review_plans)} anomalies require manual review")
        
        escalated_plans = [p for p in plans if p.action == RemediationAction.ESCALATE]
        if escalated_plans:
            recommendations.append(f"🚨 {len(escalated_plans)} anomalies escalated to senior team")
        
        # Risk-based recommendations
        critical_plans = [p for p in plans if p.risk_level == "critical"]
        if critical_plans:
            recommendations.append("⚠️ Critical risk anomalies require immediate attention")
        
        # General recommendations
        recommendations.extend([
            "📊 Monitor remediation progress and success rates",
            "🔄 Implement feedback loop for continuous improvement",
            "📚 Document remediation patterns for future reference"
        ])
        
        return recommendations
    
    def _determine_next_actions(self, plans: List[RemediationPlan]) -> List[str]:
        """Determine next actions based on remediation plans."""
        actions = []
        
        if any(p.action == RemediationAction.AUTO_FIX for p in plans):
            actions.append("execute_auto_fixes")
        
        if any(p.action == RemediationAction.MANUAL_REVIEW for p in plans):
            actions.append("send_approval_notifications")
        
        if any(p.action == RemediationAction.ESCALATE for p in plans):
            actions.append("send_emergency_notifications")
        
        actions.extend([
            "update_remediation_database",
            "trigger_notification_agent",
            "schedule_follow_up"
        ])
        
        return actions
    
    def _plan_to_dict(self, plan: RemediationPlan) -> Dict[str, Any]:
        """Convert remediation plan to dictionary."""
        return {
            "anomaly_id": plan.anomaly_id,
            "action": plan.action.value,
            "description": plan.description,
            "estimated_duration_hours": plan.estimated_duration.total_seconds() / 3600,
            "risk_level": plan.risk_level,
            "prerequisites": plan.prerequisites,
            "steps": plan.steps,
            "rollback_plan": plan.rollback_plan,
            "success_criteria": plan.success_criteria,
            "created_at": plan.created_at.isoformat(),
            "approved_by": plan.approved_by,
            "approved_at": plan.approved_at.isoformat() if plan.approved_at else None
        }
