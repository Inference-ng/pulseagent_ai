"""Application Configuration — Loaded from .env"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """FastAPI Application Settings"""

    # Database
    database_url: str = "postgresql://user:password@localhost/purseagent_dev"

    # API Keys & LLM
    google_api_key: str = ""
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # Application
    secret_key: str = "dev-secret-key"
    environment: str = "development"
    debug: bool = True
    app_name: str = "PurseAgent AI"
    app_version: str = "1.0.0"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    class Config:
        """Pydantic config"""
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
