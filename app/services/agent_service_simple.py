"""Simplified Agent workflow service without Celery."""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

import structlog
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Dataset, Run, Anomaly
from app.services.validation_service import ValidationService
from app.services.llm_service import LLMService
from app.services.mcp_service import MCPService

logger = structlog.get_logger(__name__)


class SimpleAgentService:
    """Simplified agent service for synchronous execution."""

    def __init__(self):
        self.validation_service = ValidationService()
        self.llm_service = LLMService()
        self.mcp_service = MCPService()

    async def run_workflow(
        self, dataset_id: int, include_llm_explanation: bool = True
    ) -> Dict[str, Any]:
        """Run the complete agent workflow for a dataset synchronously."""
        db = SessionLocal()
        try:
            # Get dataset
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise ValueError(f"Dataset {dataset_id} not found")

            # Create a new run
            run = Run(
                dataset_id=dataset_id, status="running", run_time=datetime.utcnow()
            )
            db.add(run)
            db.commit()
            db.refresh(run)

            logger.info("Starting agent workflow", run_id=run.id, dataset_id=dataset_id)
            # Step 1: Fetch and validate data
            validation_result = await self.validation_service.validate_dataset(
                dataset, db
            )
            print("validation_result: ", validation_result)
            # Step 2: Analyze results and detect anomalies
            anomalies = validation_result.get("anomalies", [])
            print("anomalies:", anomalies)
            # Step 3: Generate LLM explanations for anomalies
            if include_llm_explanation and anomalies:
                await self._generate_anomaly_explanations(anomalies, db)

            # Step 4: Plan and execute actions
            actions_taken = await self._plan_and_execute_actions(anomalies, dataset, db)
            print("actions_taken:", actions_taken)
            # Step 5: Update run status and summary
            run.status = "completed"
            run.duration_seconds = (datetime.utcnow() - run.run_time).total_seconds()
            run.summary = {
                "health_score": validation_result.get("health_score", 0.0),
                "anomalies_detected": len(anomalies),
                "actions_taken": actions_taken,
                "validation_summary": validation_result.get("summary", {}),
            }
            db.commit()

            logger.info(
                "Agent workflow completed",
                run_id=run.id,
                health_score=validation_result.get("health_score", 0.0),
                anomalies_detected=len(anomalies),
                actions_taken=len(actions_taken),
            )
            print(
                {
                    "run_id": run.id,
                    "status": "completed",
                    "health_score": validation_result.get("health_score", 0.0),
                    "anomalies_detected": len(anomalies),
                    "actions_taken": len(actions_taken),
                    "summary": run.summary,
                }
            )
            return {
                "run_id": run.id,
                "status": "completed",
                "health_score": validation_result.get("health_score", 0.0),
                "anomalies_detected": len(anomalies),
                "actions_taken": len(actions_taken),
                "summary": run.summary,
            }

        except Exception as e:
            logger.error("Agent workflow failed", dataset_id=dataset_id, error=str(e))
            if run:
                run.status = "failed"
                run.summary = {"error": str(e)}
                db.commit()
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
                    # Execute action
                    result = await self._execute_action(action, anomaly, dataset)
                    actions_taken.append(
                        {
                            "anomaly_id": anomaly_id,
                            "action_type": action["type"],
                            "result": result,
                        }
                    )

                    # Update anomaly status
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
        """Determine appropriate action for an anomaly."""
        # Simple rule-based action determination
        if anomaly.severity >= 4:
            return {
                "type": "create_issue",
                "priority": "high",
                "assignee": dataset.owner or "data-team",
            }
        elif anomaly.severity >= 3:
            return {
                "type": "notify_owner",
                "priority": "medium",
                "recipient": dataset.owner or "data-team",
            }
        elif anomaly.severity >= 2:
            return {"type": "auto_fix", "priority": "low"}
        else:
            return {"type": "no_action", "priority": "low"}

    async def _execute_action(
        self, action: Dict[str, Any], anomaly: Anomaly, dataset: Dataset
    ) -> Dict[str, Any]:
        """Execute the determined action."""
        try:
            action_type = action["type"]

            if action_type == "create_issue":
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
