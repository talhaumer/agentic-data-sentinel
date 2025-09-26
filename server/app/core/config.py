"""Core configuration for Data Sentinel server."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Basic app settings
    app_name: str = "Data Sentinel"
    debug: bool = False
    version: str = "0.1.0"
    
    # Database
    database_url: str = "sqlite:///./sentinel.db"
    
    # LLM Configuration
    llm_provider: str = "openai"  # openai, groq
    llm_model: str = "gpt-4o-mini"  # Default model for OpenAI
    llm_api_key: Optional[str] = None
    
    # Legacy support for separate API keys
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # GitHub Integration
    github_token: Optional[str] = None
    github_owner: Optional[str] = None
    github_repo: Optional[str] = None
    
    # Jira Integration
    jira_url: Optional[str] = None
    jira_username: Optional[str] = None
    jira_password: Optional[str] = None
    
    # Salesforce Integration
    salesforce_token: Optional[str] = None
    salesforce_instance_url: Optional[str] = None
    
    # Slack Integration
    slack_webhook_url: Optional[str] = None
    slack_bot_token: Optional[str] = None
    
    # Teams Integration
    teams_webhook_url: Optional[str] = None
    
    # Email Integration
    gmail_email: Optional[str] = None
    gmail_access_token: Optional[str] = None
    gmail_refresh_token: Optional[str] = None
    
    # Data processing
    batch_size: int = 1000
    sample_size: int = 10000
    
    # Data warehouse connections
    snowflake_account: Optional[str] = None
    snowflake_username: Optional[str] = None
    snowflake_password: Optional[str] = None
    snowflake_warehouse: Optional[str] = None
    snowflake_database: Optional[str] = None
    snowflake_schema: Optional[str] = None
    
    bigquery_project_id: Optional[str] = None
    bigquery_credentials_path: Optional[str] = None
    
    redshift_host: Optional[str] = None
    redshift_port: Optional[int] = None
    redshift_database: Optional[str] = None
    redshift_username: Optional[str] = None
    redshift_password: Optional[str] = None
    
    postgres_host: Optional[str] = None
    postgres_port: Optional[int] = None
    postgres_database: Optional[str] = None
    postgres_username: Optional[str] = None
    postgres_password: Optional[str] = None
    
    mysql_host: Optional[str] = None
    mysql_port: Optional[int] = None
    mysql_database: Optional[str] = None
    mysql_username: Optional[str] = None
    mysql_password: Optional[str] = None
    
    # Cloud storage
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    aws_region: Optional[str] = None
    
    gcs_credentials: Optional[str] = None
    gcs_project_id: Optional[str] = None
    
    azure_connection_string: Optional[str] = None
    
    # Additional settings for compatibility
    dw_conn_string: Optional[str] = None
    redis_url: Optional[str] = None
    secret_key: Optional[str] = None
    algorithm: Optional[str] = None
    access_token_expire_minutes: Optional[int] = None
    langchain_api_key: Optional[str] = None
    langchain_tracing_v2: Optional[bool] = None
    langchain_project: Optional[str] = None
    environment: Optional[str] = None
    log_level: Optional[str] = None
    max_workers: Optional[int] = None
    prometheus_port: Optional[int] = None
    dw_sample_size: Optional[int] = None
    anomaly_threshold: Optional[float] = None
    health_score_threshold: Optional[float] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
