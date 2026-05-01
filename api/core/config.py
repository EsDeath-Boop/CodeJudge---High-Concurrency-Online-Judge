from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CodeJudge"
    DEBUG: bool = False
    SECRET_KEY: str = "changeme-use-strong-secret-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://codejudge:codejudge@localhost:5432/codejudge"
    DATABASE_URL_SYNC: str = "postgresql://codejudge:codejudge@localhost:5432/codejudge"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    worker_threads: int = 4
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "codejudge-testcases"

    # Judge settings
    DEFAULT_TIME_LIMIT: int = 5       # seconds
    DEFAULT_MEMORY_LIMIT: int = 256   # MB
    MAX_CODE_LENGTH: int = 65536      # 64KB

    # Docker
    DOCKER_NETWORK: str = "none"
    SANDBOX_IMAGE_CPP: str = "codejudge-cpp"
    SANDBOX_IMAGE_PYTHON: str = "codejudge-python"
    SANDBOX_IMAGE_JAVA: str = "codejudge-java"

    class Config:
        env_file = ".env"


settings = Settings()
