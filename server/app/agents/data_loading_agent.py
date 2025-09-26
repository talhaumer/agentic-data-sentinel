"""Data Loading Agent for loading existing datasets."""

from typing import Dict, Any, Optional
import pandas as pd
import json
import sqlite3
from pathlib import Path
from .base_agent import BaseAgent, AgentContext, AgentResult, AgentStatus
from ..models import Dataset
from sqlalchemy.orm import Session
import structlog

logger = structlog.get_logger(__name__)


class DataLoadingAgent(BaseAgent):
    """Agent for loading data from existing datasets."""
    
    def __init__(self):
        super().__init__(
            name="data_loading_agent",
            description="Loads data from existing datasets for quality analysis"
        )
    
    async def can_handle(self, context: AgentContext) -> bool:
        """Check if agent can handle the context."""
        return context.dataset_id is not None
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Load data from the specified dataset."""
        try:
            # Get dataset from database
            from ..core.database import get_db
            db = next(get_db())
            dataset = db.query(Dataset).filter(Dataset.id == context.dataset_id).first()
            
            if not dataset:
                return AgentResult(
                    agent_name=self.name,
                    status=AgentStatus.FAILED,
                    data={},
                    error=f"Dataset {context.dataset_id} not found"
                )
            
            # Load data based on source type
            data = await self._load_dataset_data(dataset)
            
            if data is None or data.empty:
                return AgentResult(
                    agent_name=self.name,
                    status=AgentStatus.FAILED,
                    data={},
                    error="No data loaded from dataset"
                )
            
            # Basic data info
            data_info = {
                "rows": len(data),
                "columns": len(data.columns),
                "column_names": list(data.columns),
                "data_types": data.dtypes.to_dict(),
                "memory_usage": data.memory_usage(deep=True).sum(),
                "sample_data": data.head(5).to_dict('records')
            }
            
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                data={
                    "dataset_id": dataset.id,
                    "dataset_name": dataset.name,
                    "data_info": data_info,
                    "loaded_data": data
                },
                confidence=0.9,
                recommendations=[
                    "Data loaded successfully",
                    "Ready for quality validation"
                ],
                next_actions=[
                    "trigger_validation_agent"
                ]
            )
            
        except Exception as e:
            logger.error("Data loading failed", error=str(e))
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                data={},
                error=str(e)
            )
    
    async def _load_dataset_data(self, dataset: Dataset) -> Optional[pd.DataFrame]:
        """Load data from dataset based on source type."""
        try:
            source_config = json.loads(dataset.source_config)
            
            if dataset.source_type == "file":
                return await self._load_file_data(source_config)
            elif dataset.source_type == "database":
                return await self._load_database_data(source_config)
            else:
                logger.warning(f"Unsupported source type: {dataset.source_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load data from dataset {dataset.id}", error=str(e))
            return None
    
    async def _load_file_data(self, source_config: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Load data from file."""
        try:
            file_path = source_config.get("file_path")
            file_type = source_config.get("file_type", "csv")
            
            # Make path absolute if it's relative
            if file_path and not Path(file_path).is_absolute():
                # Go up one level from server directory to project root
                project_root = Path(__file__).parent.parent.parent.parent
                file_path = project_root / file_path
            
            if not file_path or not Path(file_path).exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            if file_type == "csv":
                return pd.read_csv(file_path)
            elif file_type == "parquet":
                return pd.read_parquet(file_path)
            elif file_type == "json":
                return pd.read_json(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load file data", error=str(e))
            return None
    
    async def _load_database_data(self, source_config: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Load data from database."""
        try:
            database_type = source_config.get("database_type", "sqlite")
            database_path = source_config.get("database_path")
            tables = source_config.get("tables", [])
            
            # Make database path absolute if it's relative
            if database_path and not Path(database_path).is_absolute():
                project_root = Path(__file__).parent.parent.parent.parent
                database_path = project_root / database_path
            
            if database_type == "sqlite" and database_path and Path(database_path).exists():
                # Load data from SQLite
                conn = sqlite3.connect(database_path)
                
                if tables:
                    # Load from specific tables
                    all_data = []
                    for table in tables:
                        try:
                            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                            df['_source_table'] = table
                            all_data.append(df)
                        except Exception as e:
                            logger.warning(f"Failed to load table {table}", error=str(e))
                    
                    if all_data:
                        return pd.concat(all_data, ignore_index=True)
                else:
                    # Load from first available table
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    table_names = cursor.fetchall()
                    
                    if table_names:
                        table_name = table_names[0][0]
                        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                
                conn.close()
            else:
                logger.warning(f"Database not found or unsupported: {database_path}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load database data", error=str(e))
            return None
