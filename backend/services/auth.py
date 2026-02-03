"""
API Key authentication service
"""

from fastapi import Header, HTTPException, status
import os
from typing import Optional


# Get API keys from environment
def get_allowed_api_keys() -> list[str]:
    """Get allowed API keys from environment variable"""
    api_keys_str = os.getenv("API_KEYS", "")
    if not api_keys_str or api_keys_str.strip() == "":
        return []
    return [key.strip() for key in api_keys_str.split(",") if key.strip()]


# Development mode check
def is_dev_mode() -> bool:
    """Check if running in development mode (no API keys configured)"""
    return len(get_allowed_api_keys()) == 0


async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> bool:
    """
    Verify API Key from request header

    In development mode (no API_KEYS configured), authentication is skipped.
    In production mode, a valid API key must be provided.
    """
    allowed_keys = get_allowed_api_keys()

    # Development mode: skip authentication
    if is_dev_mode():
        return True

    # Production mode: require valid API key
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required. Provide X-API-Key header.",
        )

    if x_api_key not in allowed_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )

    return True


async def verify_api_key_optional(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> Optional[str]:
    """
    Optional API Key verification for endpoints that work without authentication
    but can provide enhanced features with valid key
    """
    allowed_keys = get_allowed_api_keys()

    # If no keys configured, return None (dev mode)
    if not allowed_keys:
        return None

    # If key provided, validate it
    if x_api_key:
        if x_api_key in allowed_keys:
            return x_api_key
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )

    # Key not provided but not required
    return None
