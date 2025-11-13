#!/usr/bin/env python3
"""
Simple script to set up Telegram webhook
Run after deploying to production
"""

import sys
import asyncio
from app.config import get_settings
from app.oauth.telegram_webhook import set_webhook, get_webhook_info

async def main():
    settings = get_settings()

    webhook_url = f"{settings.BASE_URL}/auth/telegram/webhook"

    print("=" * 50)
    print("Telegram Webhook Setup")
    print("=" * 50)
    print(f"\nBot: @{settings.TELEGRAM_BOT_USERNAME}")
    print(f"Webhook URL: {webhook_url}")
    print()

    # Get current webhook info
    print("Checking current webhook...")
    info = await get_webhook_info()

    if info:
        current_url = info.get('url', 'Not set')
        print(f"Current webhook: {current_url}")
        print()

    # Set new webhook
    print(f"Setting webhook to: {webhook_url}")
    success = await set_webhook(webhook_url)

    if success:
        print("✅ Webhook set successfully!")
        print()
        print("Test your bot:")
        print(f"1. Open Telegram and search for @{settings.TELEGRAM_BOT_USERNAME}")
        print("2. Send /start command")
        print("3. Bot should respond")
    else:
        print("❌ Failed to set webhook!")
        print("Check your TELEGRAM_BOT_TOKEN and BASE_URL in .env")
        sys.exit(1)

    print()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
