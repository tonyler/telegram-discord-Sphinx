import httpx
import secrets
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

pending_auth_codes = {}


class TelegramAuthError(Exception):
    pass


def generate_auth_code(user_session_id: str) -> str:
    auth_code = secrets.token_urlsafe(32)
    pending_auth_codes[auth_code] = {
        "user_session_id": user_session_id,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=15)
    }
    return auth_code


def get_authorization_url(auth_code: str) -> str:
    bot_username = settings.TELEGRAM_BOT_USERNAME
    return f"https://t.me/{bot_username}?start={auth_code}"


def verify_auth_code(auth_code: str) -> Optional[Dict]:
    if auth_code not in pending_auth_codes:
        return None

    auth_data = pending_auth_codes[auth_code]
    if datetime.now() > auth_data["expires_at"]:
        del pending_auth_codes[auth_code]
        return None

    return auth_data


def complete_authorization(auth_code: str, telegram_user: Dict) -> str:
    auth_data = verify_auth_code(auth_code)
    if not auth_data:
        raise TelegramAuthError("Invalid or expired authorization code")

    del pending_auth_codes[auth_code]
    return auth_data["user_session_id"]


async def get_bot_info() -> Optional[Dict]:
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code != 200:
                return None

            data = response.json()
            return data.get("result")
    except Exception:
        return None


async def send_message(chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                error_data = response.text
                logger.error(f"Telegram sendMessage failed: {response.status_code} - {error_data}")
            else:
                logger.info(f"Message sent successfully to chat_id: {chat_id}")
            return response.status_code == 200
    except httpx.TimeoutException:
        logger.error("Telegram API timeout during send message")
        return False
    except httpx.RequestError as e:
        logger.error(f"Telegram API request error during send message: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during Telegram send message: {e}")
        return False


async def process_bot_callback(auth_code: str, telegram_user_data: Dict) -> Tuple[str, Dict]:
    user_session_id = complete_authorization(auth_code, telegram_user_data)
    return user_session_id, telegram_user_data


def cleanup_expired_codes():
    now = datetime.now()
    expired = [
        code for code, data in pending_auth_codes.items()
        if now > data["expires_at"]
    ]

    for code in expired:
        del pending_auth_codes[code]
