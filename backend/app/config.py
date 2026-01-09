import logging
import logging.config
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 기본 설정
    project_name: str = "SleepFM Backend API"
    project_version: str = "0.1.0"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000

    # 데이터베이스
    database_url: str = "postgresql://postgres:postgres@localhost:5432/sleepfm"
    database_echo: bool = False

    # JWT 설정
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # CORS 설정
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # S3/스토리지 설정
    storage_type: str = "local"  # "local" or "s3"
    storage_path: str = "./data"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_s3_bucket: str = "sleepfm-data"
    aws_region: str = "us-east-1"

    # 로깅 설정
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


settings = Settings()


def setup_logging() -> None:
    """로깅 설정"""
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": str(log_path),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "app": {"level": settings.log_level, "handlers": ["console", "file"]},
            "uvicorn": {"level": "INFO", "handlers": ["console"]},
            "uvicorn.access": {"level": "INFO", "handlers": ["console"]},
            "sqlalchemy": {"level": "WARNING", "handlers": ["console"]},
        },
        "root": {"level": settings.log_level, "handlers": ["console", "file"]},
    }

    logging.config.dictConfig(logging_config)
