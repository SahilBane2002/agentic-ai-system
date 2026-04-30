# import os
# from functools import lru_cache

# try:
#     from arcade.client import Arcade # can use from arcade.client import Arcade.  
# except Exception as e:
#     raise RuntimeError("Install the Arcade SDK: pip install arcade-client") from e

# @lru_cache
# def get_arcade_client() -> "Arcade":
#     api_key = os.getenv("ARCADE_API_KEY")
#     if not api_key:
#         raise RuntimeError("ARCADE_API_KEY not set")
#     return Arcade(api_key=api_key)

# ARCADE_USER_ID = os.getenv("ARCADE_USER_ID", "bane.s@northeastern.edu")

# app/services/arcade.py
import os
from functools import lru_cache

ARCADE_USER_ID = os.getenv("ARCADE_USER_ID", "local-user@example.com")

@lru_cache
def get_arcade_client():
    api_key = os.getenv("ARCADE_API_KEY")
    if not api_key:
        raise RuntimeError("ARCADE_API_KEY not set")
    # Lazy import so app can start even if package missing
    try:
        from arcadepy import Arcade
    except Exception as e:
        raise RuntimeError("Arcade SDK missing. Run: pip install arcadepy") from e
    return Arcade(api_key=api_key)
