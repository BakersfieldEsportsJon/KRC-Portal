from pydantic_settings import BaseSettings
from pydantic import Field
import os


class WorkerSettings(BaseSettings):
    """Worker configuration settings"""

    # App config
    APP_ENV: str = Field(default="development", description="Application environment")
    TZ: str = Field(default="America/Los_Angeles", description="Application timezone")

    # Database
    DATABASE_URL: str = Field(..., description="Database connection URL")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # Zapier Integration
    ZAPIER_CATCH_HOOK_URL: str = Field(default="", description="Zapier webhook URL")
    ZAPIER_HMAC_SECRET: str = Field(default="", description="Zapier HMAC secret")
    ZAPIER_MODE: str = Field(default="dev_log", description="Zapier mode: production or dev_log")

    # Textla
    TEXTLA_SENDER: str = Field(default="+18668849961", description="Textla sender phone number")

    # ggLeap
    GGLEAP_API_KEY: str = Field(default="", description="ggLeap API key")
    GGLEAP_BASE_URL: str = Field(default="https://api.ggleap.com", description="ggLeap API base URL")

    # Feature flags
    FEATURE_MESSAGING: bool = Field(default=True, description="Enable messaging features")
    FEATURE_GGLEAP_SYNC: bool = Field(default=False, description="Enable ggLeap sync")

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.APP_ENV == "production"


# Global settings instance
worker_settings = WorkerSettings()