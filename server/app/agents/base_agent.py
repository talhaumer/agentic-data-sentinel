"""Base agent class for all Data Sentinel agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"


class Priority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class AgentContext:
    """Context shared between agents."""
    dataset_id: Optional[int] = None
    dataset_name: Optional[str] = None
    warehouse_type: Optional[str] = None
    run_id: Optional[int] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AgentResult:
    """Result from agent execution."""
    agent_name: str
    status: AgentStatus
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time: Optional[float] = None
    confidence: float = 0.0
    recommendations: List[str] = None
    next_actions: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        if self.next_actions is None:
            self.next_actions = []


class BaseAgent(ABC):
    """Base class for all Data Sentinel agents."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.last_execution = None
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.logger = structlog.get_logger(self.name)
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the agent's main logic."""
        pass
    
    @abstractmethod
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if this agent can handle the given context."""
        pass
    
    async def validate_context(self, context: AgentContext) -> bool:
        """Validate the input context."""
        return True
    
    async def pre_execute(self, context: AgentContext) -> None:
        """Pre-execution setup."""
        self.status = AgentStatus.RUNNING
        self.last_execution = datetime.utcnow()
        self.execution_count += 1
        self.logger.info("Agent execution started", context=context.metadata)
    
    async def post_execute(self, result: AgentResult) -> None:
        """Post-execution cleanup."""
        if result.status == AgentStatus.COMPLETED:
            self.success_count += 1
            self.status = AgentStatus.COMPLETED
        else:
            self.failure_count += 1
            self.status = AgentStatus.FAILED
        
        self.logger.info(
            "Agent execution completed",
            status=result.status.value,
            execution_time=result.execution_time
        )
    
    async def run(self, context: AgentContext) -> AgentResult:
        """Run the agent with full lifecycle management."""
        start_time = datetime.utcnow()
        
        try:
            # Validate context
            if not await self.validate_context(context):
                return AgentResult(
                    agent_name=self.name,
                    status=AgentStatus.FAILED,
                    data={},
                    error="Invalid context"
                )
            
            # Check if agent can handle this context
            if not await self.can_handle(context):
                return AgentResult(
                    agent_name=self.name,
                    status=AgentStatus.FAILED,
                    data={},
                    error="Agent cannot handle this context"
                )
            
            # Pre-execution
            await self.pre_execute(context)
            
            # Execute main logic
            result = await self.execute(context)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result.execution_time = execution_time
            
            # Post-execution
            await self.post_execute(result)
            
            return result
            
        except Exception as e:
            self.logger.error("Agent execution failed", error=str(e))
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                data={},
                error=str(e),
                execution_time=execution_time
            )
            
            await self.post_execute(result)
            return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_count / max(self.execution_count, 1),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None
        }
    
    def reset_stats(self) -> None:
        """Reset agent statistics."""
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_execution = None
        self.status = AgentStatus.IDLE
