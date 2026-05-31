from functools import lru_cache
from groq import AsyncGroq
from app.config import settings


@lru_cache(maxsize=1)
def get_groq_client() -> AsyncGroq:
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set")
    return AsyncGroq(api_key=settings.groq_api_key)
