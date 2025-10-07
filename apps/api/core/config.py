from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import yaml
import os


class Settings(BaseSettings):
    """Application settings"""

    # App config
    APP_ENV: str = Field(default="development", description="Application environment")
    SECRET_KEY: str = Field(..., description="Application secret key")
    TZ: str = Field(default="America/Los_Angeles", description="Application timezone")

    # API config
    API_TITLE: str = Field(default="BEC CRM API", description="API title")
    API_DESCRIPTION: str = Field(default="Customer Relationship Management and Check-in System", description="API description")
    API_VERSION: str = Field(default="v1", description="API version")

    # Database
    DATABASE_URL: str = Field(..., description="Database connection URL")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # JWT Authentication
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration in minutes")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration in days")

    # CORS
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173"], description="CORS allowed origins")

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

    # Production hostnames
    ADMIN_HOSTNAME: str = Field(default="krc.bakersfieldesports.com", description="Admin interface hostname")
    KIOSK_HOSTNAME: str = Field(default="kiosk.bakersfieldesports.com", description="Kiosk interface hostname")

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

    def load_app_config(self) -> dict:
        """Load app configuration from YAML file"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "app.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        return {}

    def load_modules_config(self) -> dict:
        """Load modules configuration from YAML file"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "modules.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        return {"modules": {}}


# Global settings instance
settings = Settings()