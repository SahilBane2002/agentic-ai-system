import logging
import os
from pydantic import BaseModel

logger = logging.getLogger("app.config")


class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "dev")
    base_url: str = os.getenv("BASE_URL", "http://localhost:8000")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
    api_key: str = os.getenv("API_KEY", "")
    arcade_api_key: str = os.getenv("ARCADE_API_KEY", "")
    arcade_user_id: str = os.getenv("ARCADE_USER_ID", "local-user@example.com")

    @property
    def arcade_enabled(self) -> bool:
        return bool(self.arcade_api_key)


settings = Settings()


def validate_required_settings() -> None:
    missing_hard = []
    if not settings.groq_api_key:
        missing_hard.append("GROQ_API_KEY")
    if settings.app_env == "prod" and not settings.api_key:
        missing_hard.append("API_KEY")
    if missing_hard:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_hard)}")

    if not settings.arcade_api_key:
        logger.warning(
            "ARCADE_API_KEY not set — Gmail/Calendar tools will use mock implementations"
        )
