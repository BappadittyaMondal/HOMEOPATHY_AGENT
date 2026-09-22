"""
Enterprise Configuration Management for HOMEOPATHY_AGENT.
Governed by Zero-Trust principles and lightweight Hostinger VPS / Local Edge operational profiles.
Uses pure Pydantic v2 BaseModel with environment variable overrides (Zero extra dependencies).
"""
from pathlib import Path
from pydantic import BaseModel, Field
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseModel):
    # System Identity
    PROJECT_NAME: str = "HOMEOPATHY_AGENT"
    VERSION: str = "3.0.0-ENTERPRISE-CLINICAL"
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("APP_ENV", "production"))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("APP_DEBUG", "false").lower() in ("true", "1"))
    
    # Base Directories
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    REPERTORY_DIR: Path = BASE_DIR / "data" / "repertory"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # SQLite High-Concurrency WAL Engine Configuration
    DATABASE_PATH: Path = BASE_DIR / "data" / "homeopathy_hospital.db"
    SQLITE_TIMEOUT_SECONDS: float = 30.0
    SQLITE_BUSY_TIMEOUT_MS: int = 30000
    SQLITE_WAL_SYNCHRONOUS: str = "NORMAL"
    
    # Asynchronous Commit Outbox Worker
    WRITE_QUEUE_MAX_SIZE: int = 5000
    COMMIT_BATCH_SIZE: int = 50
    COMMIT_INTERVAL_MS: int = 25
    
    # Clinical Safety & DRE Settings
    FAIL_CLOSED_SAFETY: bool = True
    MAX_SIMILLIMUM_CANDIDATES: int = 25
    MIN_CONFIDENCE_THRESHOLD: float = 0.70
    
    # NCH / NABH Statutory Compliance
    RMP_SIGNATURE_MANDATORY: bool = True
    DEFAULT_JURISDICTION: str = "IN"
    ABDM_GATEWAY_URL: str = "https://dev.abdm.gov.in/gateway/v0.5"
    
    # Security & Zero-Trust
    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", 
            "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
        )
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12-hour hospital shift tokens
    ALGORITHM: str = "HS256"

# Instantiate singleton settings
settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.REPERTORY_DIR, exist_ok=True)
os.makedirs(settings.LOGS_DIR, exist_ok=True)
