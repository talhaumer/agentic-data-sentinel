"""Application configuration settings."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    dw_conn_string: str = Field(..., env="DW_CONN_STRING")

    # Redis Configuration (optional for v1)
    redis_url: str = Field("memory://", env="REDIS_URL")

    # LLM Configuration
    llm_api_key: str = Field(..., env="LLM_API_KEY")
    llm_provider: str = Field("openai", env="LLM_PROVIDER")  # openai or groq
    llm_model: str = Field("gpt-4", env="LLM_MODEL")

    # Authentication
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # External Integrations
    
    # Email Integration
    gmail_email: Optional[str] = Field(None, env="GMAIL_EMAIL")
    gmail_password: Optional[str] = Field(None, env="GMAIL_PASSWORD")
    sendgrid_api_key: Optional[str] = Field(None, env="SENDGRID_API_KEY")
    from_email: Optional[str] = Field(None, env="FROM_EMAIL")
    
    # GitHub Integration
    github_token: Optional[str] = Field(None, env="GITHUB_TOKEN")
    github_owner: Optional[str] = Field(None, env="GITHUB_OWNER")
    github_repo: Optional[str] = Field(None, env="GITHUB_REPO")
    
    
    # LangChain Tracing
    langchain_api_key: Optional[str] = Field(None, env="LANGCHAIN_API_KEY")
    langchain_tracing_v2: bool = Field(True, env="LANGCHAIN_TRACING_V2")
    langchain_project: str = Field("data-sentinel", env="LANGCHAIN_PROJECT")
    environment: str = Field("development", env="ENVIRONMENT")

    # Application Settings
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_workers: int = Field(4, env="MAX_WORKERS")
    batch_size: int = Field(1000, env="BATCH_SIZE")

    # Monitoring
    prometheus_port: int = Field(8001, env="PROMETHEUS_PORT")

    # Data Warehouse Settings
    dw_sample_size: int = Field(10000, env="DW_SAMPLE_SIZE")
    anomaly_threshold: float = Field(0.7, env="ANOMALY_THRESHOLD")
    health_score_threshold: float = Field(0.8, env="HEALTH_SCORE_THRESHOLD")
    
    # Data Quality Validation Thresholds
    # Null rate thresholds
    null_rate_critical: float = Field(0.01, env="NULL_RATE_CRITICAL")  # 1% for critical columns
    null_rate_optional: float = Field(0.3, env="NULL_RATE_OPTIONAL")   # 30% for optional columns
    null_rate_default: float = Field(0.1, env="NULL_RATE_DEFAULT")     # 10% for regular columns
    
    # Uniqueness thresholds
    uniqueness_id_columns: float = Field(0.95, env="UNIQUENESS_ID")        # 95% for ID columns
    uniqueness_categorical: float = Field(0.05, env="UNIQUENESS_CATEGORICAL")  # 5% for categorical
    uniqueness_boolean: float = Field(0.01, env="UNIQUENESS_BOOLEAN")      # 1% for boolean
    uniqueness_date: float = Field(0.8, env="UNIQUENESS_DATE")            # 80% for date columns
    uniqueness_numeric: float = Field(0.7, env="UNIQUENESS_NUMERIC")      # 70% for numeric
    uniqueness_default: float = Field(0.3, env="UNIQUENESS_DEFAULT")      # 30% for general
    
    # Outlier thresholds
    outlier_threshold: float = Field(0.05, env="OUTLIER_THRESHOLD")       # 5% outlier threshold

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
