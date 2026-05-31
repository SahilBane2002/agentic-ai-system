from functools import lru_cache

from app.config import settings

ARCADE_USER_ID = settings.arcade_user_id


@lru_cache
def get_arcade_client():
    if not settings.arcade_api_key:
        raise RuntimeError(
            "ARCADE_API_KEY not set — set it in your environment or use mock tools"
        )
    try:
        from arcadepy import Arcade
    except Exception as e:
        raise RuntimeError("Arcade SDK missing. Run: pip install arcadepy") from e
    return Arcade(api_key=settings.arcade_api_key)
