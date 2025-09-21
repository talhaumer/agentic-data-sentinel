"""Simplified Agent workflow service without Celery."""

from typing import Dict, Any, List
from datetime import datetime

import structlog
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Dataset, Run, Anomaly
from app.services.validation_service import ValidationService
from app.services.llm_service import LLMService
from app.services.mcp_service import MCPService
from app.agents.langgraph_agent import DataQualityAgent
from app.observability.metrics import MetricsCollector

logger = structlog.get_logger(__name__)


class SimpleAgentService:
    """Simplified agent service for synchronous execution."""

    def __init__(self):
        self.validation_service = ValidationService()
        self.llm_service = LLMService()
        self.mcp_service = MCPService()
        self.langgraph_agent = DataQualityAgent()
        self.metrics = MetricsCollector()

    async def run_workflow(
        self, dataset_id: int, include_llm_explanation: bool = True
    ) -> Dict[str, Any]:
        """Run the complete agent workflow for a dataset using LangGraph."""
        start_time = datetime.utcnow()
        db = SessionLocal()
        run = None
        
        try:
            # Get dataset
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise ValueError(f"Dataset {dataset_id} not found")

            # Create a new run
            run = Run(
                dataset_id=dataset_id, status="running", run_time=start_time
            )
            db.add(run)
            db.commit()
            db.refresh(run)

            logger.info("Starting LangGraph agent workflow", run_id=run.id, dataset_id=dataset_id)
            
            # Run LangGraph agent workflow
            result = await self.langgraph_agent.run_workflow(dataset_id)
            
            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Record metrics
            self.metrics.record_workflow(
                dataset_id=dataset_id,
                status=result.get("status", "failed"),
                duration=duration
            )
            
            if result.get("health_score"):
                self.metrics.record_health_score(dataset_id, result["health_score"])
            
            # Update run status and summary
            run.status = result.get("status", "failed")
            run.duration_seconds = duration
            run.summary = {
                "health_score": result.get("health_score", 0.0),
                "anomalies_detected": result.get("anomalies_detected", 0),
                "actions_executed": result.get("actions_executed", 0),
                "error": result.get("error"),
                "agent_type": "langgraph"
            }
            db.commit()

            logger.info(
                "LangGraph agent workflow completed",
                run_id=run.id,
                status=result.get("status"),
                health_score=result.get("health_score", 0.0),
                anomalies_detected=result.get("anomalies_detected", 0),
                actions_executed=result.get("actions_executed", 0),
            )

            return {
                "run_id": run.id,
                "status": result.get("status", "failed"),
                "health_score": result.get("health_score", 0.0),
                "anomalies_detected": result.get("anomalies_detected", 0),
                "actions_executed": result.get("actions_executed", 0),
                "summary": run.summary,
                "duration_seconds": duration,
                "agent_type": "langgraph"
            }

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error("LangGraph agent workflow failed", dataset_id=dataset_id, error=str(e))
            
            # Record failed workflow metrics
            self.metrics.record_workflow(
                dataset_id=dataset_id,
                status="failed",
                duration=duration
            )
            
            if run:
                run.status = "failed"
                run.duration_seconds = duration
                run.summary = {"error": str(e), "agent_type": "langgraph"}
                db.commit()
            else:
                # If run was never created, create a failed run record
                try:
                    failed_run = Run(
                        dataset_id=dataset_id,
                        status="failed",
                        run_time=start_time,
                        duration_seconds=duration,
                        summary={"error": str(e), "agent_type": "langgraph"},
                    )
                    db.add(failed_run)
                    db.commit()
                except Exception as db_error:
                    logger.error(
                        "Failed to create failed run record", error=str(db_error)
                    )
            raise
        finally:
            db.close()

    async def _generate_anomaly_explanations(
        self, anomalies: List[Dict[str, Any]], db: Session
    ):
        """Generate LLM explanations for detected anomalies."""
        try:
            for anomaly_info in anomalies:
                anomaly_id = anomaly_info.get("id")
                if not anomaly_id:
                    continue

                # Get full anomaly record
                anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
                if not anomaly:
                    continue

                # Generate explanation
                explanation = await self.llm_service.explain_anomaly(anomaly)

                # Update anomaly with explanation
                anomaly.llm_explanation = explanation.explanation
                anomaly.suggested_sql = explanation.suggested_sql
                anomaly.action_taken = explanation.action_type
                db.commit()

                logger.info("Generated explanation for anomaly", anomaly_id=anomaly_id)

        except Exception as e:
            logger.error("Failed to generate anomaly explanations", error=str(e))

    async def _plan_and_execute_actions(
        self, anomalies: List[Dict[str, Any]], dataset: Dataset, db: Session
    ) -> List[Dict[str, Any]]:
        """Plan and execute actions based on anomalies."""
        actions_taken = []

        try:
            for anomaly_info in anomalies:
                anomaly_id = anomaly_info.get("id")
                if not anomaly_id:
                    continue

                # Get full anomaly record
                anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
                if not anomaly:
                    continue

                # Determine action based on severity and type
                action = await self._determine_action(anomaly, dataset)

                if action["type"] != "no_action":
                    # Execute action or queue for approval
                    result = await self._execute_action(action, anomaly, dataset)
                    actions_taken.append(
                        {
                            "anomaly_id": anomaly_id,
                            "action_type": action["type"],
                            "suggested_action": action.get("suggested_action"),
                            "result": result,
                        }
                    )

                    # Update anomaly status based on action type
                    if action["type"] == "pending_approval":
                        anomaly.action_taken = "pending_approval"
                        anomaly.status = "pending_approval"
                    else:
                        anomaly.action_taken = action["type"]
                        if result.get("success"):
                            anomaly.status = "investigating"
                    db.commit()

        except Exception as e:
            logger.error("Failed to plan and execute actions", error=str(e))

        return actions_taken

    async def _determine_action(
        self, anomaly: Anomaly, dataset: Dataset
    ) -> Dict[str, Any]:
        """Determine appropriate action for an anomaly with human-in-the-loop."""
        # Human-in-the-loop approach - all actions require approval
        if anomaly.severity >= 4:
            return {
                "type": "pending_approval",
                "suggested_action": "create_issue",
                "priority": "high",
                "assignee": dataset.owner or "data-team",
                "reason": "High severity anomaly requires immediate attention",
                "requires_approval": True,
            }
        elif anomaly.severity >= 3:
            return {
                "type": "pending_approval",
                "suggested_action": "notify_owner",
                "priority": "medium",
                "recipient": dataset.owner or "data-team",
                "reason": "Medium severity anomaly needs review",
                "requires_approval": True,
            }
        elif anomaly.severity >= 2:
            return {
                "type": "pending_approval",
                "suggested_action": "auto_fix",
                "priority": "low",
                "reason": "Low severity anomaly can be auto-fixed with approval",
                "requires_approval": True,
            }
        else:
            return {
                "type": "no_action",
                "priority": "low",
                "reason": "Very low severity - no action needed",
            }

    async def _execute_action(
        self, action: Dict[str, Any], anomaly: Anomaly, dataset: Dataset
    ) -> Dict[str, Any]:
        """Execute the determined action."""
        try:
            action_type = action["type"]

            if action_type == "pending_approval":
                # Queue action for human approval
                return {
                    "success": True,
                    "message": "Action queued for human approval",
                    "pending_approval": True,
                    "suggested_action": action.get("suggested_action"),
                    "reason": action.get("reason"),
                    "priority": action.get("priority"),
                    "anomaly_id": anomaly.id,
                    "dataset_name": dataset.name,
                }

            elif action_type == "create_issue":
                return await self.mcp_service.create_issue(
                    title=f"Data Quality Issue: {anomaly.issue_type} in {dataset.name}",
                    description=anomaly.description,
                    priority=action.get("priority", "medium"),
                    assignee=action.get("assignee"),
                )

            elif action_type == "notify_owner":
                return await self.mcp_service.send_notification(
                    channel="#data-quality",
                    message=f"Data quality issue detected in {dataset.name}: {anomaly.description}",
                    priority=action.get("priority", "medium"),
                )

            elif action_type == "auto_fix":
                return await self._attempt_auto_fix(anomaly, dataset)

            else:
                return {"success": False, "message": "No action taken"}

        except Exception as e:
            logger.error(
                "Failed to execute action", action_type=action["type"], error=str(e)
            )
            return {"success": False, "error": str(e)}

    async def approve_action(
        self, anomaly_id: int, approved: bool, approved_by: str = "human"
    ) -> Dict[str, Any]:
        """Handle human approval for pending actions."""
        db = SessionLocal()
        try:
            # Get anomaly
            anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
            if not anomaly:
                return {"success": False, "message": "Anomaly not found"}

            if approved:
                # Execute the suggested action
                if anomaly.action_taken == "pending_approval":
                    # Get the suggested action from the anomaly's extra data or determine it
                    suggested_action = self._get_suggested_action_from_anomaly(anomaly)

                    if suggested_action == "create_issue":
                        result = await self.mcp_service.create_issue(
                            title=f"Data Quality Issue: {anomaly.issue_type}",
                            description=anomaly.description,
                            priority="high" if anomaly.severity >= 4 else "medium",
                        )
                    elif suggested_action == "notify_owner":
                        result = await self.mcp_service.send_notification(
                            channel="#data-quality",
                            message=f"Data quality issue detected: {anomaly.description}",
                            priority="high" if anomaly.severity >= 4 else "medium",
                        )
                    elif suggested_action == "auto_fix":
                        result = await self._attempt_auto_fix(anomaly, None)
                    else:
                        result = {
                            "success": False,
                            "message": "Unknown suggested action",
                        }

                    # Update anomaly status
                    anomaly.status = (
                        "resolved" if result.get("success") else "investigating"
                    )
                    anomaly.action_taken = f"approved_{suggested_action}"
                    db.commit()

                    logger.info(
                        "Action approved and executed",
                        anomaly_id=anomaly_id,
                        approved_by=approved_by,
                        action=suggested_action,
                    )

                    return {
                        "success": True,
                        "message": f"Action approved and executed: {suggested_action}",
                        "result": result,
                    }
            else:
                # Reject the action
                anomaly.status = "ignored"
                anomaly.action_taken = "rejected"
                db.commit()

                logger.info(
                    "Action rejected", anomaly_id=anomaly_id, rejected_by=approved_by
                )

                return {
                    "success": True,
                    "message": "Action rejected",
                    "result": {"success": False, "message": "Action rejected by human"},
                }

        except Exception as e:
            logger.error(
                "Failed to process approval", anomaly_id=anomaly_id, error=str(e)
            )
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def _get_suggested_action_from_anomaly(self, anomaly: Anomaly) -> str:
        """Get suggested action from anomaly data."""
        # This could be stored in anomaly.extra or determined by severity
        if anomaly.severity >= 4:
            return "create_issue"
        elif anomaly.severity >= 3:
            return "notify_owner"
        elif anomaly.severity >= 2:
            return "auto_fix"
        else:
            return "no_action"

    async def _attempt_auto_fix(
        self, anomaly: Anomaly, dataset: Dataset
    ) -> Dict[str, Any]:
        """Attempt to automatically fix an anomaly."""
        try:
            logger.info(
                "Auto-fix attempted",
                anomaly_id=anomaly.id,
                issue_type=anomaly.issue_type,
                suggested_sql=anomaly.suggested_sql,
            )

            return {
                "success": True,
                "message": "Auto-fix attempted (placeholder implementation)",
                "suggested_sql": anomaly.suggested_sql,
            }

        except Exception as e:
            logger.error("Auto-fix failed", anomaly_id=anomaly.id, error=str(e))
            return {"success": False, "error": str(e)}
