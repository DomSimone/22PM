"""
22PM AI Engine — Configuration
================================
Loads environment variables and configures LLM providers.
Create a .env file in this directory with your API keys.

Free-tier API keys:
  - Gemini: https://aistudio.google.com/app/apikey
  - Groq: https://console.groq.com
"""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    # LLM API Keys
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # LLM Models (free tier defaults)
    GEMINI_MODEL: str = "gemini-1.5-flash"       # 60 req/min free
    GROQ_MODEL: str = "llama3-70b-8192"          # 30 req/min free

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Rate limits (free tier)
    GEMINI_RATE_LIMIT_RPM: int = 60
    GROQ_RATE_LIMIT_RPM: int = 30
    GROQ_RATE_LIMIT_TPM: int = 6000

    # Default timeouts
    LLM_TIMEOUT_SECONDS: int = 30
    EMAIL_DAILY_LIMIT: int = 10  # Gmail free tier

    def __init__(self):
        """Load settings from .env file or environment variables."""
        self._load_dotenv()
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", self.GEMINI_MODEL)
        self.GROQ_MODEL = os.getenv("GROQ_MODEL", self.GROQ_MODEL)
        self.HOST = os.getenv("HOST", self.HOST)
        self.PORT = int(os.getenv("PORT", str(self.PORT)))
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    def _load_dotenv(self):
        """Load .env file if it exists."""
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip("\"'")
                        if key not in os.environ:
                            os.environ[key] = value

    def is_configured(self) -> bool:
        """Check if at least one LLM provider is configured."""
        return bool(self.GEMINI_API_KEY) or bool(self.GROQ_API_KEY)

    def get_active_providers(self) -> list[str]:
        """Return list of configured providers."""
        providers = []
        if self.GEMINI_API_KEY:
            providers.append("gemini")
        if self.GROQ_API_KEY:
            providers.append("groq")
        return providers


# Global settings instance
settings = Settings()