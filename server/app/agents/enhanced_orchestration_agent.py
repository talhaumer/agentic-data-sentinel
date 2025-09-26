"""Enhanced Orchestration Agent with parallel execution and intelligent routing."""

from typing import Dict, Any, List, Optional, Tuple
import asyncio
from datetime import datetime
from enum import Enum
import json

from .base_agent import AgentContext, AgentResult, AgentStatus, Priority
from .data_loading_agent import DataLoadingAgent
from .intelligent_validation_agent import IntelligentValidationAgent
from .intelligent_anomaly_detection_agent import IntelligentAnomalyDetectionAgent
from .remediation_agent import RemediationAgent
from .notification_agent import NotificationAgent
from .learning_agent import LearningAgent
from ..services.intelligent_llm_service import IntelligentLLMService
from ..utils.json_encoder import custom_jsonable_encoder
import structlog

logger = structlog.get_logger(__name__)


class WorkflowStrategy(Enum):
    """Workflow execution strategies."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"
    INTELLIGENT = "intelligent"


class EnhancedDataSentinelOrchestrator:
    """Enhanced orchestrator with parallel execution and intelligent routing."""
    
    def __init__(self):
        self.agents = {
            "data_loading": DataLoadingAgent(),
            "validation": IntelligentValidationAgent(),
            "anomaly_detection": IntelligentAnomalyDetectionAgent(),
            "remediation": RemediationAgent(),
            "notification": NotificationAgent(),
            "learning": LearningAgent()
        }
        self.llm_service = IntelligentLLMService()
        self.workflow_history = []
        self.performance_metrics = {}
        self.learning_memory = {}
    
    async def run_workflow(self, dataset_id: int, dataset_name: str = None, 
                          strategy: WorkflowStrategy = WorkflowStrategy.INTELLIGENT,
                          include_llm_explanation: bool = True) -> Dict[str, Any]:
        """Run enhanced workflow with intelligent routing and parallel execution."""
        try:
            workflow_id = f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            logger.info("Starting enhanced workflow", workflow_id=workflow_id, dataset_id=dataset_id)
            
            # Initialize workflow state
            initial_state = {
                "workflow_id": workflow_id,
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "strategy": strategy.value,
                "workflow_status": "running",
                "current_step": "start",
                "started_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "include_llm_explanation": include_llm_explanation,
                    "parallel_execution": strategy in [WorkflowStrategy.PARALLEL, WorkflowStrategy.INTELLIGENT]
                },
                "results": {},
                "performance": {},
                "errors": []
            }
            
            # Execute workflow based on strategy
            if strategy == WorkflowStrategy.SEQUENTIAL:
                final_state = await self._execute_sequential_workflow(initial_state)
            elif strategy == WorkflowStrategy.PARALLEL:
                final_state = await self._execute_parallel_workflow(initial_state)
            elif strategy == WorkflowStrategy.ADAPTIVE:
                final_state = await self._execute_adaptive_workflow(initial_state)
            else:  # INTELLIGENT
                final_state = await self._execute_intelligent_workflow(initial_state)
            
            # Store workflow history
            self.workflow_history.append(final_state)
            
            # Learn from workflow execution
            await self._learn_from_workflow_execution(final_state)
            
            # Generate workflow optimization suggestions
            optimization_suggestions = await self.llm_service.suggest_workflow_optimization(
                self.workflow_history[-10:]  # Last 10 workflows
            )
            
            return {
                "workflow_id": workflow_id,
                "status": final_state["workflow_status"],
                "results": custom_jsonable_encoder(final_state["results"]),
                "performance": custom_jsonable_encoder(final_state["performance"]),
                "optimization_suggestions": custom_jsonable_encoder(optimization_suggestions),
                "execution_time": self._calculate_execution_time(final_state),
                "confidence": self._calculate_workflow_confidence(final_state)
            }
            
        except Exception as e:
            logger.error("Enhanced workflow execution failed", error=str(e))
            return {
                "workflow_id": workflow_id if 'workflow_id' in locals() else "unknown",
                "status": "failed",
                "error": str(e)
            }
    
    async def _execute_sequential_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow sequentially (original behavior)."""
        execution_path = [
            "data_loading", "validation", "anomaly_detection", 
            "remediation", "notification", "learning"
        ]
        
        for step in execution_path:
            try:
                state = await self._execute_step(step, state)
                if state["workflow_status"] == "failed":
                    break
            except Exception as e:
                logger.error(f"Step {step} failed", error=str(e))
                state["workflow_status"] = "failed"
                state["errors"].append(f"Step {step}: {str(e)}")
                break
        
        return state
    
    async def _execute_parallel_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with parallel execution where possible."""
        # Step 1: Data loading (must be sequential)
        state = await self._execute_step("data_loading", state)
        if state["workflow_status"] == "failed":
            return state
        
        # Step 2: Parallel validation and preparation
        validation_task = asyncio.create_task(self._execute_step("validation", state))
        anomaly_prep_task = asyncio.create_task(self._prepare_anomaly_detection(state))
        
        validation_state, anomaly_prep_state = await asyncio.gather(
            validation_task, anomaly_prep_task, return_exceptions=True
        )
        
        if isinstance(validation_state, Exception):
            state["workflow_status"] = "failed"
            state["errors"].append(f"Validation failed: {str(validation_state)}")
            return state
        
        state = validation_state
        
        # Step 3: Anomaly detection with prepared context
        if not isinstance(anomaly_prep_state, Exception):
            state.update(anomaly_prep_state)
        
        state = await self._execute_step("anomaly_detection", state)
        if state["workflow_status"] == "failed":
            return state
        
        # Step 4: Parallel remediation and notification
        remediation_task = asyncio.create_task(self._execute_step("remediation", state))
        notification_task = asyncio.create_task(self._execute_step("notification", state))
        
        remediation_state, notification_state = await asyncio.gather(
            remediation_task, notification_task, return_exceptions=True
        )
        
        if isinstance(remediation_state, Exception):
            state["workflow_status"] = "failed"
            state["errors"].append(f"Remediation failed: {str(remediation_state)}")
            return state
        
        state = remediation_state
        
        # Step 5: Learning (sequential)
        state = await self._execute_step("learning", state)
        
        return state
    
    async def _execute_adaptive_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with adaptive strategy based on data characteristics."""
        # Analyze data characteristics to determine optimal strategy
        data_characteristics = await self._analyze_data_characteristics(state)
        
        if data_characteristics.get("size", 0) > 100000:  # Large dataset
            # Use parallel execution for large datasets
            return await self._execute_parallel_workflow(state)
        elif data_characteristics.get("complexity", "low") == "high":
            # Use intelligent execution for complex datasets
            return await self._execute_intelligent_workflow(state)
        else:
            # Use sequential execution for simple datasets
            return await self._execute_sequential_workflow(state)
    
    async def _execute_intelligent_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with AI-powered intelligent routing and execution."""
        # Step 1: Intelligent data loading
        state = await self._execute_step("data_loading", state)
        if state["workflow_status"] == "failed":
            return state
        
        # Step 2: AI-powered analysis and planning
        analysis = await self.llm_service.analyze_data_quality(
            state["results"].get("data_loading", {}).get("loaded_data"),
            {"dataset_id": state["dataset_id"], "workflow_type": "intelligent"}
        )
        
        # Step 3: Dynamic workflow planning
        workflow_plan = await self._create_dynamic_workflow_plan(analysis, state)
        
        # Step 4: Execute planned workflow
        for step_info in workflow_plan:
            if step_info.get("parallel", False):
                # Execute parallel steps
                parallel_tasks = []
                for parallel_step in step_info["steps"]:
                    task = asyncio.create_task(self._execute_step(parallel_step, state))
                    parallel_tasks.append(task)
                
                results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        state["errors"].append(f"Parallel step {step_info['steps'][i]}: {str(result)}")
                    else:
                        state = result
            else:
                # Execute sequential step
                state = await self._execute_step(step_info["step"], state)
            
            if state["workflow_status"] == "failed":
                break
        
        # Final status check - consider workflow successful if core steps completed
        if state["workflow_status"] != "completed":
            core_steps_success = (
                state["results"].get("data_loading", {}).get("status") == "completed" and
                state["results"].get("validation", {}).get("status") == "completed"
            )
            if core_steps_success:
                state["workflow_status"] = "completed"
                logger.info("Workflow marked as completed - core steps succeeded")
        
        return state
    
    async def _execute_step(self, step: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        start_time = datetime.utcnow()
        
        try:
            if step == "start":
                state["current_step"] = "data_loading"
                state["metadata"]["workflow_started_at"] = datetime.utcnow().isoformat()
                return state
            
            elif step == "data_loading":
                context = AgentContext(
                    dataset_id=state["dataset_id"],
                    dataset_name=state["dataset_name"]
                )
                
                agent = self.agents["data_loading"]
                result = await agent.run(context)
                
                state["results"]["data_loading"] = {
                    "status": result.status.value,
                    "data": result.data,
                    "confidence": result.confidence
                }
                
                if result.status == AgentStatus.COMPLETED:
                    state["current_step"] = "validation"
                    # Pass loaded data to context for next steps
                    state["loaded_data"] = result.data.get("loaded_data")
                    # Also store in results for easy access
                    state["results"]["loaded_data"] = result.data.get("loaded_data")
                else:
                    state["workflow_status"] = "failed"
                    state["errors"].append(f"Data loading failed: {result.error}")
                
                return state
            
            elif step == "validation":
                context = AgentContext(
                    dataset_id=state["dataset_id"],
                    dataset_name=state["dataset_name"]
                )
                # Set loaded data as an attribute on the context
                context.loaded_data = state.get("loaded_data")
                
                agent = self.agents["validation"]
                result = await agent.run(context)
                
                state["results"]["validation"] = {
                    "status": result.status.value,
                    "data": result.data,
                    "confidence": result.confidence
                }
                
                if result.status == AgentStatus.COMPLETED:
                    state["current_step"] = "anomaly_detection"
                else:
                    state["workflow_status"] = "failed"
                    state["errors"].append(f"Validation failed: {result.error}")
                
                return state
            
            elif step == "anomaly_detection":
                context = AgentContext(
                    dataset_id=state["dataset_id"],
                    dataset_name=state["dataset_name"]
                )
                # Set loaded data as an attribute on the context
                context.loaded_data = state.get("loaded_data")
                
                agent = self.agents["anomaly_detection"]
                result = await agent.run(context)
                
                state["results"]["anomaly_detection"] = {
                    "status": result.status.value,
                    "data": result.data,
                    "confidence": result.confidence
                }
                
                if result.status == AgentStatus.COMPLETED:
                    state["current_step"] = "remediation"
                else:
                    # Log the error but continue workflow
                    state["errors"].append(f"Anomaly detection failed: {result.error}")
                    logger.warning("Anomaly detection failed, continuing workflow", error=result.error)
                    state["current_step"] = "remediation"  # Continue to next step
                
                return state
            
            elif step == "remediation":
                context = AgentContext(
                    dataset_id=state["dataset_id"],
                    dataset_name=state["dataset_name"]
                )
                
                agent = self.agents["remediation"]
                result = await agent.run(context)
                
                state["results"]["remediation"] = {
                    "status": result.status.value,
                    "data": result.data,
                    "confidence": result.confidence
                }
                
                if result.status == AgentStatus.COMPLETED:
                    state["current_step"] = "notification"
                else:
                    # Log the error but continue workflow
                    state["errors"].append(f"Remediation failed: {result.error}")
                    logger.warning("Remediation failed, continuing workflow", error=result.error)
                    state["current_step"] = "notification"  # Continue to next step
                
                return state
            
            elif step == "notification":
                context = AgentContext(
                    dataset_id=state["dataset_id"],
                    dataset_name=state["dataset_name"]
                )
                
                agent = self.agents["notification"]
                result = await agent.run(context)
                
                state["results"]["notification"] = {
                    "status": result.status.value,
                    "data": result.data,
                    "confidence": result.confidence
                }
                
                if result.status == AgentStatus.COMPLETED:
                    state["current_step"] = "learning"
                else:
                    # Log the error but continue workflow
                    state["errors"].append(f"Notification failed: {result.error}")
                    logger.warning("Notification failed, continuing workflow", error=result.error)
                    state["current_step"] = "learning"  # Continue to next step
                
                return state
            
            elif step == "learning":
                context = AgentContext(
                    dataset_id=state["dataset_id"],
                    dataset_name=state["dataset_name"]
                )
                
                agent = self.agents["learning"]
                result = await agent.run(context)
                
                state["results"]["learning"] = {
                    "status": result.status.value,
                    "data": result.data,
                    "confidence": result.confidence
                }
                
                if result.status == AgentStatus.COMPLETED:
                    state["current_step"] = "end"
                    state["workflow_status"] = "completed"
                else:
                    # Log the error but mark workflow as completed if core steps succeeded
                    state["errors"].append(f"Learning failed: {result.error}")
                    logger.warning("Learning failed, but workflow completed", error=result.error)
                    state["current_step"] = "end"
                    state["workflow_status"] = "completed"  # Mark as completed anyway
                
                return state
            
            else:
                state["workflow_status"] = "failed"
                state["errors"].append(f"Unknown step: {step}")
                return state
        
        except Exception as e:
            logger.error(f"Step {step} execution failed", error=str(e))
            state["workflow_status"] = "failed"
            state["errors"].append(f"Step {step}: {str(e)}")
            return state
        
        finally:
            # Record performance metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            state["performance"][step] = execution_time
    
    async def _prepare_anomaly_detection(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for anomaly detection."""
        return {
            "anomaly_detection_prepared": True,
            "preparation_time": datetime.utcnow().isoformat()
        }
    
    async def _analyze_data_characteristics(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data characteristics for adaptive workflow planning."""
        loaded_data = state.get("loaded_data")
        if loaded_data is None:
            return {"size": 0, "complexity": "unknown"}
        
        return {
            "size": len(loaded_data),
            "columns": len(loaded_data.columns),
            "complexity": "high" if len(loaded_data.columns) > 10 else "low",
            "data_types": str(loaded_data.dtypes.to_dict())
        }
    
    async def _create_dynamic_workflow_plan(self, analysis: Dict[str, Any], state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create dynamic workflow plan based on AI analysis."""
        plan = []
        
        # Always start with data loading
        plan.append({"step": "data_loading", "parallel": False})
        
        # Based on analysis, determine if validation and anomaly detection can run in parallel
        if analysis.get("complexity", "low") == "low":
            plan.append({
                "parallel": True,
                "steps": ["validation", "anomaly_detection"]
            })
        else:
            plan.append({"step": "validation", "parallel": False})
            plan.append({"step": "anomaly_detection", "parallel": False})
        
        # Remediation and notification can often run in parallel
        plan.append({
            "parallel": True,
            "steps": ["remediation", "notification"]
        })
        
        # Learning is always sequential
        plan.append({"step": "learning", "parallel": False})
        
        return plan
    
    async def _learn_from_workflow_execution(self, state: Dict[str, Any]) -> None:
        """Learn from workflow execution to improve future workflows."""
        learning_data = {
            "workflow_id": state["workflow_id"],
            "strategy": state["strategy"],
            "execution_time": self._calculate_execution_time(state),
            "success": state["workflow_status"] == "completed",
            "errors": state["errors"],
            "performance": state["performance"]
        }
        
        self.learning_memory[state["workflow_id"]] = learning_data
        
        # Update performance metrics
        strategy = state["strategy"]
        if strategy not in self.performance_metrics:
            self.performance_metrics[strategy] = []
        
        self.performance_metrics[strategy].append(learning_data)
    
    def _calculate_execution_time(self, state: Dict[str, Any]) -> float:
        """Calculate total workflow execution time."""
        if "started_at" in state["metadata"]:
            start_time = datetime.fromisoformat(state["metadata"]["workflow_started_at"])
            end_time = datetime.utcnow()
            return (end_time - start_time).total_seconds()
        return 0.0
    
    def _calculate_workflow_confidence(self, state: Dict[str, Any]) -> float:
        """Calculate overall workflow confidence."""
        if state["workflow_status"] != "completed":
            return 0.0
        
        # Calculate confidence based on agent results
        total_confidence = 0.0
        agent_count = 0
        
        for step, result in state["results"].items():
            if isinstance(result, dict) and "confidence" in result:
                total_confidence += result["confidence"]
                agent_count += 1
        
        if agent_count == 0:
            return 0.0
        
        return total_confidence / agent_count
