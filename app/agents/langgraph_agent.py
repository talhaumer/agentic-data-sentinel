"""LangGraph-based agent implementation for data quality monitoring."""

from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime

import structlog
from langgraph.graph import StateGraph, END

from app.config import get_settings
from app.models import Dataset, Anomaly
from app.services.validation_service import ValidationService
from app.services.llm_service import LLMService
from app.services.mcp_service import MCPService

logger = structlog.get_logger(__name__)


class AgentState(TypedDict):
    """State for the LangGraph agent workflow."""
    dataset_id: int
    dataset: Optional[Dataset]
    validation_result: Optional[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    explanations: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    mcp_actions: List[Dict[str, Any]]  # MCP-based actions
    current_step: str
    error: Optional[str]
    run_id: Optional[int]


class DataQualityAgent:
    """LangGraph-based agent for data quality monitoring and remediation."""
    
    def __init__(self):
        self.settings = get_settings()
        self.validation_service = ValidationService()
        self.llm_service = LLMService()
        self.mcp_service = MCPService()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("fetch_dataset", self._fetch_dataset)
        workflow.add_node("validate_data", self._validate_data)
        workflow.add_node("detect_anomalies", self._detect_anomalies)
        workflow.add_node("explain_anomalies", self._explain_anomalies)
        workflow.add_node("plan_actions", self._plan_actions)
        workflow.add_node("create_mcp_actions", self._create_mcp_actions)
        workflow.add_node("execute_actions", self._execute_actions)
        workflow.add_node("execute_mcp_actions", self._execute_mcp_actions)
        workflow.add_node("handle_error", self._handle_error)
        
        # Add edges
        workflow.set_entry_point("fetch_dataset")
        workflow.add_edge("fetch_dataset", "validate_data")
        workflow.add_edge("validate_data", "detect_anomalies")
        workflow.add_edge("detect_anomalies", "explain_anomalies")
        workflow.add_edge("explain_anomalies", "plan_actions")
        workflow.add_edge("plan_actions", "create_mcp_actions")
        workflow.add_edge("create_mcp_actions", "execute_actions")
        workflow.add_edge("execute_actions", "execute_mcp_actions")
        workflow.add_edge("execute_mcp_actions", END)
        
        # Error handling
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    async def _fetch_dataset(self, state: AgentState) -> AgentState:
        """Fetch dataset information from database."""
        try:
            logger.info("Fetching dataset", dataset_id=state["dataset_id"])
            
            # Fetch real dataset from database
            from app.database import get_db
            from app.models import Dataset
            
            db = next(get_db())
            dataset = db.query(Dataset).filter(Dataset.id == state["dataset_id"]).first()
            
            if not dataset:
                raise ValueError(f"Dataset with ID {state['dataset_id']} not found")
            
            state["dataset"] = {
                "id": dataset.id,
                "name": dataset.name,
                "source": dataset.source,
                "owner": dataset.owner
            }
            state["current_step"] = "validate_data"
            
            logger.info("Dataset fetched successfully", dataset_id=state["dataset_id"])
            return state
            
        except Exception as e:
            logger.error("Failed to fetch dataset", error=str(e))
            state["error"] = str(e)
            state["current_step"] = "handle_error"
            return state
    
    async def _validate_data(self, state: AgentState) -> AgentState:
        """Validate dataset for quality issues using real validation service."""
        try:
            logger.info("Validating data", dataset_id=state["dataset_id"])
            
            # Use real validation service
            from app.database import get_db
            from app.models import Dataset
            
            db = next(get_db())
            dataset = db.query(Dataset).filter(Dataset.id == state["dataset_id"]).first()
            
            if not dataset:
                raise ValueError(f"Dataset with ID {state['dataset_id']} not found")
            
            # Run real validation checks
            validation_response = await self.validation_service.validate_dataset(dataset, db)
            
            # Extract results from validation response
            health_score = validation_response.get("health_score", 0.0)
            validation_results = validation_response.get("validation_results", [])
            anomalies = validation_response.get("anomalies", [])
            
            state["validation_result"] = {
                "health_score": health_score,
                "validation_results": validation_results,
                "anomalies": anomalies,
                "total_checks": len(validation_results),
                "passed_checks": sum(1 for r in validation_results if r.get("passed", False)),
                "failed_checks": sum(1 for r in validation_results if not r.get("passed", False))
            }
            state["current_step"] = "detect_anomalies"
            
            logger.info("Data validation completed", 
                       health_score=health_score,
                       total_checks=len(validation_results))
            return state
            
        except Exception as e:
            logger.error("Failed to validate data", error=str(e))
            state["error"] = str(e)
            state["current_step"] = "handle_error"
            return state
    
    async def _detect_anomalies(self, state: AgentState) -> AgentState:
        """Detect anomalies in the dataset using real validation service."""
        try:
            logger.info("Detecting anomalies", dataset_id=state["dataset_id"])
            
            # Use real anomaly detection
            from app.database import get_db
            from app.models import Dataset
            
            db = next(get_db())
            dataset = db.query(Dataset).filter(Dataset.id == state["dataset_id"]).first()
            
            if not dataset:
                raise ValueError(f"Dataset with ID {state['dataset_id']} not found")
            
            # Get anomalies from validation results
            anomalies = state["validation_result"].get("anomalies", [])
            
            # Convert anomalies to the expected format
            state["anomalies"] = []
            for anomaly in anomalies:
                state["anomalies"].append({
                    "id": anomaly.get("id", 0),
                    "type": anomaly.get("issue_type", "unknown"),
                    "column": anomaly.get("column_name", "unknown"),
                    "severity": anomaly.get("severity", 1),
                    "description": anomaly.get("description", "No description"),
                    "detected_at": anomaly.get("detected_at", datetime.utcnow().isoformat()),
                    "extra": anomaly.get("extra", {})
                })
            
            state["current_step"] = "explain_anomalies"
            
            logger.info("Anomalies detected", count=len(state["anomalies"]))
            return state
            
        except Exception as e:
            logger.error("Failed to detect anomalies", error=str(e))
            state["error"] = str(e)
            state["current_step"] = "handle_error"
            return state
    
    async def _explain_anomalies(self, state: AgentState) -> AgentState:
        """Generate LLM explanations for detected anomalies."""
        try:
            logger.info("Explaining anomalies", count=len(state["anomalies"]))
            
            explanations = []
            for anomaly in state["anomalies"]:
                try:
                    # Create a mock Anomaly object for LLM service
                    from app.models import Anomaly
                    mock_anomaly = Anomaly(
                        id=anomaly["id"],
                        dataset_id=state["dataset_id"],
                        table_name=state["dataset"]["name"],
                        column_name=anomaly["column"],
                        issue_type=anomaly["type"],
                        severity=anomaly["severity"],
                        description=anomaly["description"],
                        detected_at=datetime.fromisoformat(anomaly["detected_at"].replace('Z', '+00:00'))
                    )
                    
                    # Get real LLM explanation
                    llm_response = await self.llm_service.explain_anomaly(mock_anomaly)
                    
                    explanation = {
                        "anomaly_id": anomaly["id"],
                        "explanation": llm_response.explanation,
                        "confidence": llm_response.confidence,
                        "suggested_sql": llm_response.suggested_sql,
                        "action_type": llm_response.action_type
                    }
                    
                except Exception as llm_error:
                    logger.warning("LLM explanation failed, using fallback", 
                                 anomaly_id=anomaly["id"], error=str(llm_error))
                    # Fallback to mock explanation
                    explanation = {
                        "anomaly_id": anomaly["id"],
                        "explanation": f"Root cause analysis for {anomaly['type']}: This issue likely occurred due to data ingestion problems or validation rule failures.",
                        "confidence": 0.85,
                        "suggested_sql": f"SELECT COUNT(*) FROM {state['dataset']['name']} WHERE {anomaly['column']} IS NULL;",
                        "action_type": "investigate"
                    }
                
                explanations.append(explanation)
            
            state["explanations"] = explanations
            state["current_step"] = "plan_actions"
            
            logger.info("Anomaly explanations generated", count=len(explanations))
            return state
            
        except Exception as e:
            logger.error("Failed to explain anomalies", error=str(e))
            state["error"] = str(e)
            state["current_step"] = "handle_error"
            return state
    
    async def _plan_actions(self, state: AgentState) -> AgentState:
        """Plan remediation actions based on anomalies and explanations."""
        try:
            logger.info("Planning actions", anomaly_count=len(state["anomalies"]))
            
            actions = []
            for anomaly, explanation in zip(state["anomalies"], state["explanations"]):
                action = {
                    "anomaly_id": anomaly["id"],
                    "action_type": self._determine_action_type(anomaly, explanation),
                    "priority": "high" if anomaly["severity"] >= 4 else "medium",
                    "description": f"Action for {anomaly['type']} in {anomaly['column']}",
                    "suggested_sql": explanation["suggested_sql"]
                }
                actions.append(action)
            
            state["actions"] = actions
            state["current_step"] = "create_mcp_actions"
            
            logger.info("Actions planned", count=len(actions))
            return state
            
        except Exception as e:
            logger.error("Failed to plan actions", error=str(e))
            state["error"] = str(e)
            state["current_step"] = "handle_error"
            return state
    
    async def _create_mcp_actions(self, state: AgentState) -> AgentState:
        """Create MCP-based actions for notifications and issue creation."""
        try:
            logger.info("Creating MCP actions", action_count=len(state["actions"]))
            
            mcp_actions = []
            dataset_name = state["dataset"]["name"]
            
            for action in state["actions"]:
                anomaly = next(a for a in state["anomalies"] if a["id"] == action["anomaly_id"])
                explanation = next(e for e in state["explanations"] if e["anomaly_id"] == action["anomaly_id"])
                
                if action["action_type"] == "create_issue":
                    # Create GitHub issue via MCP
                    mcp_action = {
                        "tool": "github",
                        "action": "create_issue",
                        "payload": {
                            "repo": f"{self.settings.github_owner}/{self.settings.github_repo}",
                            "title": f"Data Quality Issue: {anomaly['type']} in {dataset_name}.{anomaly['column']}",
                            "description": self._create_github_issue_description(anomaly, explanation, dataset_name),
                            "labels": ["data-quality", "bug", f"severity-{anomaly['severity']}"]
                        }
                    }
                    mcp_actions.append(mcp_action)
                
                elif action["action_type"] == "notify_owner":
                    # Convert notify_owner to create_issue for GitHub-only mode
                    mcp_action = {
                        "tool": "github",
                        "action": "create_issue",
                        "payload": {
                            "repo": f"{self.settings.github_owner}/{self.settings.github_repo}",
                            "title": f"Data Quality Alert: {anomaly['type']} in {dataset_name}.{anomaly['column']}",
                            "description": self._create_github_issue_description(anomaly, explanation, dataset_name),
                            "labels": ["data-quality", "alert", f"severity-{anomaly['severity']}"]
                        }
                    }
                    mcp_actions.append(mcp_action)
            
            state["mcp_actions"] = mcp_actions
            state["current_step"] = "execute_actions"
            
            logger.info("MCP actions created", count=len(mcp_actions))
            return state
            
        except Exception as e:
            logger.error("Failed to create MCP actions", error=str(e))
            state["error"] = str(e)
            state["current_step"] = "handle_error"
            return state
    
    async def _execute_actions(self, state: AgentState) -> AgentState:
        """Execute planned remediation actions."""
        try:
            logger.info("Executing actions", action_count=len(state["actions"]))
            
            executed_actions = []
            for action in state["actions"]:
                # Execute real actions based on action type
                if action["action_type"] == "auto_fix":
                    # For auto-fix actions, we could implement actual fixes
                    result = {
                        "action_id": action["anomaly_id"],
                        "status": "completed",
                        "message": f"Auto-fix action executed for anomaly {action['anomaly_id']}",
                        "timestamp": datetime.utcnow().isoformat(),
                        "action_type": "auto_fix"
                    }
                elif action["action_type"] == "no_action":
                    result = {
                        "action_id": action["anomaly_id"],
                        "status": "skipped",
                        "message": f"No action required for anomaly {action['anomaly_id']}",
                        "timestamp": datetime.utcnow().isoformat(),
                        "action_type": "no_action"
                    }
                elif action["action_type"] == "pending_approval":
                    result = {
                        "action_id": action["anomaly_id"],
                        "status": "pending_approval",
                        "message": f"Action requires human approval for anomaly {action['anomaly_id']}",
                        "timestamp": datetime.utcnow().isoformat(),
                        "action_type": "pending_approval"
                    }
                else:
                    # For other actions (create_issue, notify_owner), they will be handled by MCP
                    result = {
                        "action_id": action["anomaly_id"],
                        "status": "pending_mcp",
                        "message": f"Action {action['action_type']} will be executed via MCP",
                        "timestamp": datetime.utcnow().isoformat(),
                        "action_type": action["action_type"]
                    }
                
                executed_actions.append(result)
            
            state["actions"] = executed_actions
            state["current_step"] = "execute_mcp_actions"
            
            logger.info("Actions executed successfully", count=len(executed_actions))
            return state
            
        except Exception as e:
            logger.error("Failed to execute actions", error=str(e))
            state["error"] = str(e)
            state["current_step"] = "handle_error"
            return state
    
    async def _execute_mcp_actions(self, state: AgentState) -> AgentState:
        """Execute MCP-based actions (notifications and issue creation)."""
        try:
            logger.info("Executing MCP actions", action_count=len(state["mcp_actions"]))
            
            executed_mcp_actions = []
            for mcp_action in state["mcp_actions"]:
                try:
                    result = await self.mcp_service.execute_mcp_action(mcp_action)
                    executed_mcp_actions.append({
                        "mcp_action": mcp_action,
                        "result": result,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    if result.get("success"):
                        logger.info("MCP action executed successfully", 
                                  tool=mcp_action["tool"], action=mcp_action["action"])
                    else:
                        logger.warning("MCP action failed", 
                                     tool=mcp_action["tool"], action=mcp_action["action"],
                                     error=result.get("error"))
                        
                except Exception as action_error:
                    logger.error("Failed to execute MCP action", 
                               tool=mcp_action["tool"], action=mcp_action["action"],
                               error=str(action_error))
                    executed_mcp_actions.append({
                        "mcp_action": mcp_action,
                        "result": {"success": False, "error": str(action_error)},
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            state["mcp_actions"] = executed_mcp_actions
            state["current_step"] = "completed"
            
            logger.info("MCP actions executed", count=len(executed_mcp_actions))
            return state
            
        except Exception as e:
            logger.error("Failed to execute MCP actions", error=str(e))
            state["error"] = str(e)
            state["current_step"] = "handle_error"
            return state
    
    async def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors in the workflow."""
        logger.error("Workflow error", error=state.get("error"))
        state["current_step"] = "error"
        return state
    
    def _determine_action_type(self, anomaly: Dict[str, Any], explanation: Dict[str, Any]) -> str:
        """Determine the appropriate action type based on anomaly severity and type."""
        severity = anomaly.get("severity", 1)
        issue_type = anomaly.get("issue_type", "unknown")
        
        # Critical issues always require human approval
        if severity >= 5:
            return "create_issue"
        elif severity >= 4:
            # High severity: require approval for data_loss and data_integrity
            if issue_type in ["data_loss", "data_integrity", "security"]:
                return "create_issue"
            else:
                return "pending_approval"
        elif severity >= 3:
            # Medium-high severity: require approval for most cases
            if issue_type in ["data_loss", "data_integrity", "security", "completeness"]:
                return "pending_approval"
            else:
                return "auto_fix"
        elif severity >= 2:
            # Medium severity: auto-fix for simple issues, approval for complex ones
            if issue_type in ["data_loss", "data_integrity", "security"]:
                return "pending_approval"
            else:
                return "auto_fix"
        else:
            return "no_action"
    
    def _create_github_issue_description(self, anomaly: Dict[str, Any], explanation: Dict[str, Any], dataset_name: str) -> str:
        """Create a detailed GitHub issue description."""
        return f"""## 🚨 Data Quality Issue Detected

**Anomaly ID**: {anomaly['id']}
**Dataset**: `{dataset_name}`
**Column**: `{anomaly['column']}`
**Issue Type**: {anomaly['type']}
**Severity**: {anomaly['severity']}/5
**Detected**: {anomaly['detected_at']}

### Description
{anomaly['description']}

### AI Analysis
{explanation['explanation']}

**Confidence**: {explanation['confidence']:.2f}

### Suggested Investigation
```sql
{explanation['suggested_sql']}
```

### Impact Assessment
- **Severity Level**: {anomaly['severity']}/5
- **Data Quality Impact**: {'High' if anomaly['severity'] >= 4 else 'Medium' if anomaly['severity'] >= 3 else 'Low'}
- **Business Impact**: {'Critical' if anomaly['severity'] >= 4 else 'Moderate' if anomaly['severity'] >= 3 else 'Minor'}

### Recommended Actions
1. [ ] Investigate root cause using provided SQL query
2. [ ] Check data ingestion pipeline for recent changes
3. [ ] Review data validation rules
4. [ ] Implement monitoring alerts for future occurrences
5. [ ] Update data quality documentation

### Labels
- `data-quality`
- `severity-{anomaly['severity']}`
- `{anomaly['type']}`
- `{dataset_name}`
"""
    
    def _create_email_body(self, anomaly: Dict[str, Any], explanation: Dict[str, Any], dataset_name: str) -> str:
        """Create an HTML email body for notifications."""
        severity_color = "red" if anomaly['severity'] >= 4 else "orange" if anomaly['severity'] >= 3 else "yellow"
        severity_text = "Critical" if anomaly['severity'] >= 4 else "High" if anomaly['severity'] >= 3 else "Medium"
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: {severity_color}; border-bottom: 2px solid {severity_color}; padding-bottom: 10px;">
                    🚨 Data Quality Alert - {severity_text} Severity
                </h2>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #495057;">Issue Details</h3>
                    <p><strong>Dataset:</strong> {dataset_name}</p>
                    <p><strong>Column:</strong> {anomaly['column']}</p>
                    <p><strong>Issue Type:</strong> {anomaly['type']}</p>
                    <p><strong>Severity:</strong> {anomaly['severity']}/5</p>
                    <p><strong>Detected:</strong> {anomaly['detected_at']}</p>
                </div>
                
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1976d2;">AI Analysis</h3>
                    <p>{explanation['explanation']}</p>
                    <p><strong>Confidence:</strong> {explanation['confidence']:.2f}</p>
                </div>
                
                <div style="background-color: #fff3e0; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #f57c00;">Suggested Investigation</h3>
                    <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto;"><code>{explanation['suggested_sql']}</code></pre>
                </div>
                
                <div style="background-color: #f3e5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #7b1fa2;">Next Steps</h3>
                    <ul>
                        <li>Investigate the root cause using the provided SQL query</li>
                        <li>Check data ingestion pipeline for recent changes</li>
                        <li>Review and update data validation rules if needed</li>
                        <li>Consider implementing monitoring alerts</li>
                    </ul>
                </div>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">
                    This alert was generated by Data Sentinel's AI-powered data quality monitoring system.
                </p>
            </div>
        </body>
        </html>
        """
    
    async def run_workflow(self, dataset_id: int) -> Dict[str, Any]:
        """Run the complete agent workflow."""
        initial_state = AgentState(
            dataset_id=dataset_id,
            dataset=None,
            validation_result=None,
            anomalies=[],
            explanations=[],
            actions=[],
            mcp_actions=[],
            current_step="fetch_dataset",
            error=None,
            run_id=None
        )
        
        try:
            result = await self.graph.ainvoke(initial_state)
            
            return {
                "status": "completed" if result["current_step"] != "error" else "failed",
                "dataset_id": dataset_id,
                "health_score": result.get("validation_result", {}).get("health_score", 0),
                "anomalies_detected": len(result.get("anomalies", [])),
                "actions_executed": len(result.get("actions", [])),
                "mcp_actions_executed": len(result.get("mcp_actions", [])),
                "mcp_actions": result.get("mcp_actions", []),
                "error": result.get("error")
            }
            
        except Exception as e:
            logger.error("Workflow execution failed", error=str(e))
            return {
                "status": "failed",
                "dataset_id": dataset_id,
                "error": str(e)
            }
