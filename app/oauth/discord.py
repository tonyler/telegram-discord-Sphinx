import httpx
import logging
from typing import Dict, Optional, Tuple
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

DISCORD_API_BASE = "https://discord.com/api/v10"
DISCORD_OAUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"


class DiscordAuthError(Exception):
    pass


def get_authorization_url(state: str) -> str:
    params = {
        "client_id": settings.DISCORD_CLIENT_ID,
        "redirect_uri": settings.DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{DISCORD_OAUTH_URL}?{query}"


async def exchange_code(code: str) -> Optional[Dict]:
    data = {
        "client_id": settings.DISCORD_CLIENT_ID,
        "client_secret": settings.DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.DISCORD_REDIRECT_URI,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                DISCORD_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code != 200:
                logger.error(f"Discord token exchange failed: {response.status_code} - {response.text}")
                return None

            return response.json()
    except httpx.TimeoutException:
        logger.error("Discord API timeout during token exchange")
        return None
    except httpx.RequestError as e:
        logger.error(f"Discord API request error during token exchange: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during Discord token exchange: {e}")
        return None


async def get_user_info(access_token: str) -> Optional[Dict]:
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{DISCORD_API_BASE}/users/@me",
                headers=headers
            )

            if response.status_code != 200:
                logger.error(f"Discord get user info failed: {response.status_code}")
                return None

            return response.json()
    except httpx.TimeoutException:
        logger.error("Discord API timeout during get user info")
        return None
    except httpx.RequestError as e:
        logger.error(f"Discord API request error during get user info: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during Discord get user info: {e}")
        return None


async def refresh_access_token(refresh_token: str) -> Optional[Dict]:
    data = {
        "client_id": settings.DISCORD_CLIENT_ID,
        "client_secret": settings.DISCORD_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                DISCORD_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code != 200:
                return None

            return response.json()
    except Exception:
        return None


async def process_callback(code: str) -> Tuple[Dict, Dict]:
    token_data = await exchange_code(code)
    if not token_data:
        raise DiscordAuthError("Failed to exchange code for token")

    user_info = await get_user_info(token_data["access_token"])
    if not user_info:
        raise DiscordAuthError("Failed to get user info")

    return token_data, user_info
