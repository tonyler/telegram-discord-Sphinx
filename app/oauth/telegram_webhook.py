import httpx
from typing import Dict, Optional
from app.config import get_settings
from app.oauth import telegram_authz
from app.storage.user_storage import get_user_storage

settings = get_settings()


async def set_webhook(webhook_url: str) -> bool:
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook"
    payload = {"url": webhook_url, "allowed_updates": ["message"]}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                result = response.json()
                return result.get("ok", False)

            return False
    except Exception as e:
        print(f"Error setting webhook: {e}")
        return False


async def delete_webhook() -> bool:
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/deleteWebhook"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                result = response.json()
                return result.get("ok", False)

            return False
    except Exception:
        return False


async def get_webhook_info() -> Optional[Dict]:
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getWebhookInfo"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                result = response.json()
                return result.get("result")

            return None
    except Exception:
        return None


async def handle_update(update: Dict) -> Dict:
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"Received Telegram update: {update}")

    if "message" not in update:
        return {"ok": True, "message": "No message in update"}

    message = update["message"]
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    user = message.get("from")

    logger.info(f"Processing message from chat_id={chat_id}, text='{text}'")

    if not chat_id or not user:
        logger.error(f"Missing chat_id or user in message: {message}")
        return {"ok": False, "error": "Missing chat_id or user"}

    if text.startswith("/start "):
        auth_code = text.split(" ", 1)[1].strip()
        logger.info(f"Handling /start command with auth_code: {auth_code[:10]}...")
        return await handle_start_command(auth_code, chat_id, user)

    elif text == "/start":
        logger.info(f"Sending welcome message to chat_id: {chat_id}")
        await telegram_authz.send_message(
            chat_id,
            "👋 Welcome! To connect your Telegram account, please use the link from the website."
        )
        return {"ok": True, "message": "Sent welcome message"}

    logger.info(f"Ignoring message: {text}")
    return {"ok": True, "message": "Message ignored"}


async def handle_start_command(auth_code: str, chat_id: int, telegram_user: Dict) -> Dict:
    try:
        auth_data = telegram_authz.verify_auth_code(auth_code)
        if not auth_data:
            raise telegram_authz.TelegramAuthError("Invalid auth code")

        user_id = auth_data.get("user_id")
        if not user_id:
            raise telegram_authz.TelegramAuthError("No user_id in auth data")

        user_session_id = telegram_authz.complete_authorization(auth_code, telegram_user)

        telegram_id = str(telegram_user.get("id"))
        username = telegram_user.get("username")
        first_name = telegram_user.get("first_name", "")
        last_name = telegram_user.get("last_name", "")
        display_name = username or f"{first_name} {last_name}".strip()

        storage = get_user_storage()
        try:
            storage.bind_platform(
                user_id=user_id,
                platform="telegram",
                platform_user_id=telegram_id,
                username=display_name
            )
        except ValueError as e:
            raise telegram_authz.TelegramAuthError(str(e))

        await telegram_authz.send_message(
            chat_id,
            "✅ <b>Telegram account connected successfully!</b>\n\n"
            "You can now close this chat and return to the website.",
            parse_mode="HTML"
        )
        return {"ok": True, "message": "Authorization successful"}

    except telegram_authz.TelegramAuthError as e:
        await telegram_authz.send_message(
            chat_id,
            f"❌ <b>Authorization failed:</b> {str(e)}\n\n"
            "Please try again from the website.",
            parse_mode="HTML"
        )
        return {"ok": False, "error": str(e)}

    except Exception as e:
        await telegram_authz.send_message(
            chat_id,
            "❌ <b>An error occurred</b>\n\n"
            "Please try again later.",
            parse_mode="HTML"
        )
        return {"ok": False, "error": f"Unexpected error: {str(e)}"}
