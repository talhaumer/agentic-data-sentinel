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
    slack_webhook_url: Optional[str] = Field(None, env="SLACK_WEBHOOK_URL")
    jira_base_url: Optional[str] = Field(None, env="JIRA_BASE_URL")
    jira_username: Optional[str] = Field(None, env="JIRA_USERNAME")
    jira_api_token: Optional[str] = Field(None, env="JIRA_API_TOKEN")
    
    # GitHub Integration
    github_token: Optional[str] = Field(None, env="GITHUB_TOKEN")
    github_owner: Optional[str] = Field(None, env="GITHUB_OWNER")
    github_repo: Optional[str] = Field(None, env="GITHUB_REPO")
    
    # Email Integration
    sendgrid_api_key: Optional[str] = Field(None, env="SENDGRID_API_KEY")
    from_email: Optional[str] = Field(None, env="FROM_EMAIL")
    
    # Observability
    jaeger_agent_host: str = Field("localhost", env="JAEGER_AGENT_HOST")
    jaeger_agent_port: int = Field(14268, env="JAEGER_AGENT_PORT")
    environment: str = Field("development", env="ENVIRONMENT")

    # Application Settings
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_workers: int = Field(4, env="MAX_WORKERS")
    batch_size: int = Field(1000, env="BATCH_SIZE")

    # Monitoring
    prometheus_port: int = Field(8001, env="PROMETHEUS_PORT")
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")

    # Data Warehouse Settings
    dw_sample_size: int = Field(10000, env="DW_SAMPLE_SIZE")
    anomaly_threshold: float = Field(0.7, env="ANOMALY_THRESHOLD")
    health_score_threshold: float = Field(0.8, env="HEALTH_SCORE_THRESHOLD")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
