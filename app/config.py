from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "dev")
    base_url: str = os.getenv("BASE_URL", "http://localhost:8000")

settings = Settings()