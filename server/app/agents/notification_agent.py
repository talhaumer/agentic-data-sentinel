"""Notification & Escalation Agent for intelligent alerting and communication."""

import asyncio
import json
import structlog
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..core.config import get_settings
from .base_agent import AgentContext, AgentResult, AgentStatus, BaseAgent, Priority

logger = structlog.get_logger(__name__)


class NotificationChannel(Enum):
    """Notification channels."""
    SLACK = "slack"
    EMAIL = "email"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    SMS = "sms"
    PHONE = "phone"


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class EscalationLevel(Enum):
    """Escalation levels."""
    TEAM = "team"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"
    CTO = "cto"


@dataclass
class NotificationRule:
    """Notification rule configuration."""
    anomaly_type: str
    severity_threshold: int
    channels: List[NotificationChannel]
    recipients: List[str]
    escalation_level: EscalationLevel
    escalation_time: timedelta
    business_hours_only: bool = False
    enabled: bool = True


@dataclass
class NotificationMessage:
    """Notification message structure."""
    channel: NotificationChannel
    recipients: List[str]
    subject: str
    content: str
    priority: NotificationPriority
    metadata: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class EscalationPolicy:
    """Escalation policy configuration."""
    level: EscalationLevel
    recipients: List[str]
    channels: List[NotificationChannel]
    escalation_time: timedelta
    business_hours_only: bool
    auto_escalate: bool = True


class NotificationAgent(BaseAgent):
    """Agent for intelligent notification and escalation management."""
    
    def __init__(self):
        super().__init__(
            name="notification_agent",
            description=(
                "Manages intelligent notifications and escalation based on "
                "anomaly severity and business impact"
            )
        )
        self.settings = get_settings()
        self.notification_rules = self._initialize_notification_rules()
        self.escalation_policies = self._initialize_escalation_policies()
        self.channel_handlers = self._initialize_channel_handlers()
        self.notification_history = []
        self.escalation_timers = {}
    
    def _initialize_notification_rules(self) -> List[NotificationRule]:
        """Initialize notification rules for different scenarios."""
        return [
            NotificationRule(
                anomaly_type="quality",
                severity_threshold=3,
                channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
                recipients=["data-team@company.com"],
                escalation_level=EscalationLevel.TEAM,
                escalation_time=timedelta(hours=2)
            ),
            NotificationRule(
                anomaly_type="volume",
                severity_threshold=4,
                channels=[
                    NotificationChannel.SLACK, 
                    NotificationChannel.TEAMS, 
                    NotificationChannel.EMAIL
                ],
                recipients=["data-team@company.com", "ops-team@company.com"],
                escalation_level=EscalationLevel.MANAGER,
                escalation_time=timedelta(hours=1)
            ),
            NotificationRule(
                anomaly_type="schema",
                severity_threshold=2,
                channels=[
                    NotificationChannel.SLACK, 
                    NotificationChannel.EMAIL, 
                    NotificationChannel.PHONE
                ],
                recipients=["data-team@company.com", "dba-team@company.com"],
                escalation_level=EscalationLevel.DIRECTOR,
                escalation_time=timedelta(minutes=30)
            ),
            NotificationRule(
                anomaly_type="statistical",
                severity_threshold=5,
                channels=[NotificationChannel.SLACK],
                recipients=["data-team@company.com"],
                escalation_level=EscalationLevel.TEAM,
                escalation_time=timedelta(hours=4)
            )
        ]
    
    def _initialize_escalation_policies(self) -> Dict[EscalationLevel, EscalationPolicy]:
        """Initialize escalation policies."""
        return {
            EscalationLevel.TEAM: EscalationPolicy(
                level=EscalationLevel.TEAM,
                recipients=["data-team@company.com"],
                channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
                escalation_time=timedelta(hours=2),
                business_hours_only=False
            ),
            EscalationLevel.MANAGER: EscalationPolicy(
                level=EscalationLevel.MANAGER,
                recipients=["data-manager@company.com", "ops-manager@company.com"],
                channels=[NotificationChannel.EMAIL, NotificationChannel.TEAMS],
                escalation_time=timedelta(hours=1),
                business_hours_only=True
            ),
            EscalationLevel.DIRECTOR: EscalationPolicy(
                level=EscalationLevel.DIRECTOR,
                recipients=["data-director@company.com", "cto@company.com"],
                channels=[NotificationChannel.EMAIL, NotificationChannel.PHONE],
                escalation_time=timedelta(minutes=30),
                business_hours_only=False
            ),
            EscalationLevel.EXECUTIVE: EscalationPolicy(
                level=EscalationLevel.EXECUTIVE,
                recipients=["cto@company.com", "ceo@company.com"],
                channels=[NotificationChannel.EMAIL, NotificationChannel.PHONE, NotificationChannel.SMS],
                escalation_time=timedelta(minutes=15),
                business_hours_only=False
            )
        }
    
    def _initialize_channel_handlers(self) -> Dict[NotificationChannel, callable]:
        """Initialize channel handlers."""
        return {
            NotificationChannel.SLACK: self._send_slack_notification,
            NotificationChannel.EMAIL: self._send_email_notification,
            NotificationChannel.TEAMS: self._send_teams_notification,
            NotificationChannel.WEBHOOK: self._send_webhook_notification,
            NotificationChannel.SMS: self._send_sms_notification,
            NotificationChannel.PHONE: self._send_phone_notification
        }
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if agent can handle the context."""
        return "anomalies" in context.metadata or "remediation_plans" in context.metadata
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute notification and escalation logic."""
        try:
            # Extract anomalies and remediation plans from context
            anomalies = context.metadata.get("anomalies", [])
            remediation_plans = context.metadata.get("remediation_plans", [])
            
            if not anomalies and not remediation_plans:
                return AgentResult(
                    agent_name=self.name,
                    status=AgentStatus.FAILED,
                    data={},
                    error="No anomalies or remediation plans found in context"
                )
            
            # Process notifications
            notification_results = []
            
            # Process anomaly notifications
            for anomaly in anomalies:
                result = await self._process_anomaly_notification(anomaly, context)
                notification_results.append(result)
            
            # Process remediation notifications
            for plan in remediation_plans:
                result = await self._process_remediation_notification(plan, context)
                notification_results.append(result)
            
            # Process escalations
            escalation_results = await self._process_escalations(context)
            
            # Generate notification report
            notification_report = self._generate_notification_report(notification_results, escalation_results)
            
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "notifications_sent": len(notification_results),
                    "escalations_processed": len(escalation_results),
                    "notification_results": notification_results,
                    "escalation_results": escalation_results,
                    "notification_report": notification_report
                },
                confidence=0.95,
                recommendations=self._generate_notification_recommendations(notification_results),
                next_actions=self._determine_next_actions(notification_results, escalation_results)
            )
            
        except Exception as e:
            logger.error("Notification processing failed", error=str(e))
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                data={},
                error=str(e)
            )
    
    async def _process_anomaly_notification(self, anomaly: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Process notification for a single anomaly."""
        try:
            anomaly_type = anomaly.get("anomaly_type", "unknown")
            severity = anomaly.get("severity", 1)
            
            # Find applicable notification rules
            applicable_rules = [
                rule for rule in self.notification_rules
                if rule.enabled and rule.anomaly_type == anomaly_type and severity >= rule.severity_threshold
            ]
            
            if not applicable_rules:
                return {
                    "anomaly_id": anomaly.get("id"),
                    "status": "no_rules",
                    "message": "No notification rules applicable"
                }
            
            # Use the most specific rule (highest severity threshold)
            rule = max(applicable_rules, key=lambda r: r.severity_threshold)
            
            # Generate notification message
            message = self._generate_anomaly_message(anomaly, rule)
            
            # Send notifications through all channels
            sent_notifications = []
            for channel in rule.channels:
                try:
                    result = await self._send_notification(message, channel, rule.recipients)
                    sent_notifications.append({
                        "channel": channel.value,
                        "status": "sent" if result["success"] else "failed",
                        "error": result.get("error")
                    })
                except Exception as e:
                    logger.error(f"Failed to send {channel.value} notification", error=str(e))
                    sent_notifications.append({
                        "channel": channel.value,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Set up escalation if needed
            if rule.escalation_level != EscalationLevel.TEAM:
                await self._schedule_escalation(anomaly, rule)
            
            return {
                "anomaly_id": anomaly.get("id"),
                "status": "sent",
                "rule_applied": rule.anomaly_type,
                "channels": sent_notifications,
                "escalation_scheduled": rule.escalation_level.value
            }
            
        except Exception as e:
            logger.error(f"Anomaly notification processing failed", error=str(e))
            return {
                "anomaly_id": anomaly.get("id"),
                "status": "failed",
                "error": str(e)
            }
    
    async def _process_remediation_notification(self, plan: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Process notification for remediation plan."""
        try:
            action = plan.get("action", "unknown")
            risk_level = plan.get("risk_level", "medium")
            
            # Determine notification channels based on action and risk
            if action == "auto_fix":
                channels = [NotificationChannel.SLACK]
                priority = NotificationPriority.LOW
            elif action == "manual_review":
                channels = [NotificationChannel.SLACK, NotificationChannel.EMAIL]
                priority = NotificationPriority.MEDIUM
            elif action == "escalate":
                channels = [NotificationChannel.EMAIL, NotificationChannel.TEAMS, NotificationChannel.PHONE]
                priority = NotificationPriority.CRITICAL
            else:
                channels = [NotificationChannel.SLACK]
                priority = NotificationPriority.LOW
            
            # Generate remediation message
            message = self._generate_remediation_message(plan, priority)
            
            # Send notifications
            sent_notifications = []
            for channel in channels:
                try:
                    result = await self._send_notification(message, channel, ["data-team@company.com"])
                    sent_notifications.append({
                        "channel": channel.value,
                        "status": "sent" if result["success"] else "failed",
                        "error": result.get("error")
                    })
                except Exception as e:
                    logger.error(f"Failed to send {channel.value} notification", error=str(e))
                    sent_notifications.append({
                        "channel": channel.value,
                        "status": "failed",
                        "error": str(e)
                    })
            
            return {
                "plan_id": plan.get("anomaly_id"),
                "status": "sent",
                "action": action,
                "channels": sent_notifications
            }
            
        except Exception as e:
            logger.error(f"Remediation notification processing failed", error=str(e))
            return {
                "plan_id": plan.get("anomaly_id"),
                "status": "failed",
                "error": str(e)
            }
    
    def _generate_anomaly_message(self, anomaly: Dict[str, Any], rule: NotificationRule) -> NotificationMessage:
        """Generate notification message for anomaly."""
        anomaly_type = anomaly.get("anomaly_type", "unknown")
        severity = anomaly.get("severity", 1)
        description = anomaly.get("description", "No description available")
        confidence = anomaly.get("confidence", 0.0)
        
        # Determine priority based on severity
        priority_map = {
            1: NotificationPriority.LOW,
            2: NotificationPriority.LOW,
            3: NotificationPriority.MEDIUM,
            4: NotificationPriority.HIGH,
            5: NotificationPriority.CRITICAL
        }
        priority = priority_map.get(severity, NotificationPriority.LOW)
        
        # Generate subject
        severity_labels = {
            1: "Low", 2: "Low", 3: "Medium", 4: "High", 5: "Critical"
        }
        severity_label = severity_labels.get(severity, "Unknown")
        subject = f"🚨 Data Quality Alert - {severity_label} Severity: {anomaly_type.title()}"
        
        # Generate content
        content = f"""
**Data Quality Anomaly Detected**

**Type:** {anomaly_type.title()}
**Severity:** {severity_label} ({severity}/5)
**Confidence:** {confidence:.1%}
**Description:** {description}

**Affected Columns:** {', '.join(anomaly.get('affected_columns', []))}
**Detected At:** {anomaly.get('detected_at', datetime.utcnow().isoformat())}

**Business Impact:** {anomaly.get('business_impact', 'Unknown')}

**Suggested Actions:**
{chr(10).join(f"• {action}" for action in anomaly.get('suggested_actions', []))}

**Next Steps:**
1. Review the anomaly details
2. Assess business impact
3. Determine remediation approach
4. Monitor for similar issues

---
*This alert was generated by Data Sentinel's AI-powered monitoring system.*
        """.strip()
        
        return NotificationMessage(
            channel=rule.channels[0],  # Primary channel
            recipients=rule.recipients,
            subject=subject,
            content=content,
            priority=priority,
            metadata={
                "anomaly_id": anomaly.get("id"),
                "anomaly_type": anomaly_type,
                "severity": severity,
                "confidence": confidence,
                "rule_applied": rule.anomaly_type
            },
            created_at=datetime.utcnow()
        )
    
    def _generate_remediation_message(self, plan: Dict[str, Any], priority: NotificationPriority) -> NotificationMessage:
        """Generate notification message for remediation plan."""
        action = plan.get("action", "unknown")
        risk_level = plan.get("risk_level", "medium")
        description = plan.get("description", "No description available")
        
        # Generate subject
        action_labels = {
            "auto_fix": "🔧 Auto-Fix",
            "manual_review": "👥 Manual Review",
            "escalate": "🚨 Escalation"
        }
        action_label = action_labels.get(action, action.title())
        subject = f"{action_label} Required - {risk_level.title()} Risk"
        
        # Generate content
        content = f"""
**Remediation Plan Created**

**Action:** {action_label}
**Risk Level:** {risk_level.title()}
**Description:** {description}

**Estimated Duration:** {plan.get('estimated_duration_hours', 0):.1f} hours
**Steps:** {len(plan.get('steps', []))} steps planned

**Prerequisites:**
{chr(10).join(f"• {prereq}" for prereq in plan.get('prerequisites', []))}

**Success Criteria:**
{chr(10).join(f"• {criteria}" for criteria in plan.get('success_criteria', []))}

**Next Steps:**
1. Review the remediation plan
2. Approve or modify as needed
3. Execute the plan
4. Monitor progress

---
*This remediation plan was generated by Data Sentinel's AI system.*
        """.strip()
        
        return NotificationMessage(
            channel=NotificationChannel.EMAIL,  # Default channel
            recipients=["data-team@company.com"],
            subject=subject,
            content=content,
            priority=priority,
            metadata={
                "plan_id": plan.get("anomaly_id"),
                "action": action,
                "risk_level": risk_level
            },
            created_at=datetime.utcnow()
        )
    
    async def _send_notification(self, message: NotificationMessage, channel: NotificationChannel, recipients: List[str]) -> Dict[str, Any]:
        """Send notification through specified channel."""
        try:
            handler = self.channel_handlers.get(channel)
            if not handler:
                return {"success": False, "error": f"No handler for channel {channel.value}"}
            
            # Update message with recipients
            message.recipients = recipients
            message.channel = channel
            
            result = await handler(message)
            
            # Log notification
            self.notification_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "channel": channel.value,
                "recipients": recipients,
                "subject": message.subject,
                "success": result.get("success", False),
                "error": result.get("error")
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send {channel.value} notification", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _send_slack_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send Slack notification."""
        try:
            # Simplified implementation - would use actual Slack API
            slack_payload = {
                "channel": "#data-quality",
                "text": message.subject,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message.content
                        }
                    }
                ]
            }
            
            # Simulate API call
            await asyncio.sleep(0.1)
            
            logger.info("Slack notification sent", channel=message.channel.value)
            return {"success": True, "message": "Slack notification sent"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_email_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send email notification."""
        try:
            # Simplified implementation - would use actual email service
            email_payload = {
                "to": message.recipients,
                "subject": message.subject,
                "body": message.content,
                "priority": message.priority.value
            }
            
            # Simulate API call
            await asyncio.sleep(0.1)
            
            logger.info("Email notification sent", recipients=message.recipients)
            return {"success": True, "message": "Email notification sent"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_teams_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send Teams notification."""
        try:
            # Simplified implementation - would use actual Teams API
            teams_payload = {
                "text": message.subject,
                "sections": [
                    {
                        "activityTitle": message.subject,
                        "activityText": message.content
                    }
                ]
            }
            
            # Simulate API call
            await asyncio.sleep(0.1)
            
            logger.info("Teams notification sent", channel=message.channel.value)
            return {"success": True, "message": "Teams notification sent"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_webhook_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send webhook notification."""
        try:
            # Simplified implementation - would use actual webhook
            webhook_payload = {
                "event": "data_quality_alert",
                "data": {
                    "subject": message.subject,
                    "content": message.content,
                    "metadata": message.metadata
                }
            }
            
            # Simulate API call
            await asyncio.sleep(0.1)
            
            logger.info("Webhook notification sent", channel=message.channel.value)
            return {"success": True, "message": "Webhook notification sent"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_sms_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send SMS notification."""
        try:
            # Simplified implementation - would use actual SMS service
            sms_payload = {
                "to": message.recipients,
                "message": f"{message.subject}: {message.content[:100]}..."
            }
            
            # Simulate API call
            await asyncio.sleep(0.1)
            
            logger.info("SMS notification sent", recipients=message.recipients)
            return {"success": True, "message": "SMS notification sent"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_phone_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send phone notification."""
        try:
            # Simplified implementation - would use actual phone service
            phone_payload = {
                "to": message.recipients,
                "message": f"Data Quality Alert: {message.subject}"
            }
            
            # Simulate API call
            await asyncio.sleep(0.1)
            
            logger.info("Phone notification sent", recipients=message.recipients)
            return {"success": True, "message": "Phone notification sent"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _schedule_escalation(self, anomaly: Dict[str, Any], rule: NotificationRule) -> None:
        """Schedule escalation for anomaly."""
        try:
            escalation_time = datetime.utcnow() + rule.escalation_time
            escalation_id = f"esc_{anomaly.get('id', 'unknown')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            self.escalation_timers[escalation_id] = {
                "anomaly": anomaly,
                "rule": rule,
                "escalation_time": escalation_time,
                "status": "scheduled"
            }
            
            logger.info("Escalation scheduled", escalation_id=escalation_id, escalation_time=escalation_time)
            
        except Exception as e:
            logger.error("Failed to schedule escalation", error=str(e))
    
    async def _process_escalations(self, context: AgentContext) -> List[Dict[str, Any]]:
        """Process scheduled escalations."""
        escalation_results = []
        current_time = datetime.utcnow()
        
        for escalation_id, escalation_data in list(self.escalation_timers.items()):
            if current_time >= escalation_data["escalation_time"]:
                try:
                    result = await self._execute_escalation(escalation_id, escalation_data)
                    escalation_results.append(result)
                    
                    # Remove completed escalation
                    del self.escalation_timers[escalation_id]
                    
                except Exception as e:
                    logger.error(f"Escalation execution failed for {escalation_id}", error=str(e))
                    escalation_results.append({
                        "escalation_id": escalation_id,
                        "status": "failed",
                        "error": str(e)
                    })
        
        return escalation_results
    
    async def _execute_escalation(self, escalation_id: str, escalation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute escalation."""
        try:
            anomaly = escalation_data["anomaly"]
            rule = escalation_data["rule"]
            
            # Get escalation policy
            policy = self.escalation_policies.get(rule.escalation_level)
            if not policy:
                return {
                    "escalation_id": escalation_id,
                    "status": "failed",
                    "error": f"No escalation policy for level {rule.escalation_level.value}"
                }
            
            # Generate escalation message
            escalation_message = self._generate_escalation_message(anomaly, rule, policy)
            
            # Send escalation notifications
            sent_notifications = []
            for channel in policy.channels:
                try:
                    result = await self._send_notification(escalation_message, channel, policy.recipients)
                    sent_notifications.append({
                        "channel": channel.value,
                        "status": "sent" if result["success"] else "failed",
                        "error": result.get("error")
                    })
                except Exception as e:
                    logger.error(f"Failed to send escalation {channel.value} notification", error=str(e))
                    sent_notifications.append({
                        "channel": channel.value,
                        "status": "failed",
                        "error": str(e)
                    })
            
            return {
                "escalation_id": escalation_id,
                "status": "completed",
                "level": rule.escalation_level.value,
                "channels": sent_notifications
            }
            
        except Exception as e:
            logger.error(f"Escalation execution failed for {escalation_id}", error=str(e))
            return {
                "escalation_id": escalation_id,
                "status": "failed",
                "error": str(e)
            }
    
    def _generate_escalation_message(self, anomaly: Dict[str, Any], rule: NotificationRule, policy: EscalationPolicy) -> NotificationMessage:
        """Generate escalation message."""
        anomaly_type = anomaly.get("anomaly_type", "unknown")
        severity = anomaly.get("severity", 1)
        
        subject = f"🚨 ESCALATED: Data Quality Alert - {anomaly_type.title()}"
        
        content = f"""
**ESCALATED DATA QUALITY ALERT**

This alert has been escalated due to lack of response within the expected timeframe.

**Original Alert:**
- Type: {anomaly_type.title()}
- Severity: {severity}/5
- Detected: {anomaly.get('detected_at', 'Unknown')}
- Description: {anomaly.get('description', 'No description')}

**Escalation Details:**
- Level: {rule.escalation_level.value.title()}
- Escalated At: {datetime.utcnow().isoformat()}
- Original Recipients: {', '.join(rule.recipients)}

**Immediate Action Required:**
1. Acknowledge this escalation
2. Review the anomaly details
3. Take appropriate action
4. Update the team on resolution status

**Business Impact:**
{anomaly.get('business_impact', 'Unknown')}

---
*This escalation was triggered by Data Sentinel's automated escalation system.*
        """.strip()
        
        return NotificationMessage(
            channel=policy.channels[0],
            recipients=policy.recipients,
            subject=subject,
            content=content,
            priority=NotificationPriority.CRITICAL,
            metadata={
                "escalation_level": rule.escalation_level.value,
                "original_anomaly_id": anomaly.get("id"),
                "escalation_reason": "timeout"
            },
            created_at=datetime.utcnow()
        )
    
    def _generate_notification_report(self, notification_results: List[Dict[str, Any]], escalation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive notification report."""
        return {
            "summary": {
                "total_notifications": len(notification_results),
                "successful_notifications": len([r for r in notification_results if r.get("status") == "sent"]),
                "failed_notifications": len([r for r in notification_results if r.get("status") == "failed"]),
                "total_escalations": len(escalation_results),
                "completed_escalations": len([r for r in escalation_results if r.get("status") == "completed"])
            },
            "channel_performance": {
                "slack": len([r for r in notification_results if "slack" in str(r.get("channels", []))]),
                "email": len([r for r in notification_results if "email" in str(r.get("channels", []))]),
                "teams": len([r for r in notification_results if "teams" in str(r.get("channels", []))]),
                "webhook": len([r for r in notification_results if "webhook" in str(r.get("channels", []))])
            },
            "escalation_summary": {
                "scheduled": len(self.escalation_timers),
                "completed": len([r for r in escalation_results if r.get("status") == "completed"]),
                "failed": len([r for r in escalation_results if r.get("status") == "failed"])
            }
        }
    
    def _generate_notification_recommendations(self, notification_results: List[Dict[str, Any]]) -> List[str]:
        """Generate notification recommendations."""
        recommendations = []
        
        successful_count = len([r for r in notification_results if r.get("status") == "sent"])
        total_count = len(notification_results)
        
        if total_count > 0:
            success_rate = successful_count / total_count
            if success_rate < 0.9:
                recommendations.append(f"⚠️ Notification success rate is {success_rate:.1%} - review channel configurations")
        
        failed_notifications = [r for r in notification_results if r.get("status") == "failed"]
        if failed_notifications:
            recommendations.append(f"🔧 {len(failed_notifications)} notifications failed - check channel connectivity")
        
        # Channel-specific recommendations
        slack_count = len([r for r in notification_results if "slack" in str(r.get("channels", []))])
        if slack_count > 0:
            recommendations.append("📱 Consider setting up Slack bot for interactive notifications")
        
        email_count = len([r for r in notification_results if "email" in str(r.get("channels", []))])
        if email_count > 0:
            recommendations.append("📧 Ensure email templates are mobile-friendly")
        
        # General recommendations
        recommendations.extend([
            "📊 Monitor notification delivery rates and user engagement",
            "🔄 Implement feedback collection for notification effectiveness",
            "⚙️ Review and update notification rules based on team preferences"
        ])
        
        return recommendations
    
    def _determine_next_actions(self, notification_results: List[Dict[str, Any]], escalation_results: List[Dict[str, Any]]) -> List[str]:
        """Determine next actions based on notification results."""
        actions = []
        
        if notification_results:
            actions.append("update_notification_database")
        
        if escalation_results:
            actions.append("update_escalation_status")
        
        if self.escalation_timers:
            actions.append("monitor_scheduled_escalations")
        
        actions.extend([
            "generate_notification_metrics",
            "update_team_dashboards"
        ])
        
        return actions
