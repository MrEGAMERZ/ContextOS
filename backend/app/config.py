from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "ContextOS"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./contextos.db")
    
    # AWS Bedrock settings
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    BEDROCK_MODEL_ID_FAST: str = os.getenv("BEDROCK_MODEL_ID_FAST", "anthropic.claude-3-5-haiku-20241022-v1:0")
    BEDROCK_MODEL_ID_DEEP: str = os.getenv("BEDROCK_MODEL_ID_DEEP", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    MOCK_BEDROCK: bool = os.getenv("MOCK_BEDROCK", "true").lower() in ("true", "1", "yes")

    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
