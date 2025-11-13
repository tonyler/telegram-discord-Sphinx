from fastapi import APIRouter, HTTPException, Query, Depends, Response, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import secrets

from app.storage.user_storage import get_user_storage
from app.oauth import discord, telegram_authz
from app.oauth.telegram_webhook import handle_update
from app.session import session_manager, get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])

oauth_states = {}


@router.get("/discord")
async def discord_auth():
    state = secrets.token_urlsafe(32)
    oauth_states[state] = "discord"
    auth_url = discord.get_authorization_url(state)
    return RedirectResponse(auth_url)


@router.get("/discord/callback")
async def discord_callback(
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None)
):
    if error:
        return RedirectResponse(f"/?error=Discord authentication cancelled", status_code=303)

    if not code or not state:
        return RedirectResponse(f"/?error=Invalid authentication request", status_code=303)

    if state not in oauth_states:
        return RedirectResponse(f"/?error=Authentication session expired. Please try again.", status_code=303)

    del oauth_states[state]

    try:
        token_data, user_info = await discord.process_callback(code)
    except discord.DiscordAuthError as e:
        return RedirectResponse(f"/?error=Discord authentication failed. Please try again.", status_code=303)

    storage = get_user_storage()
    user = storage.get_user_by_platform("discord", user_info["id"])

    try:
        if user:
            user = storage.bind_platform(
                user_id=user['id'],
                platform="discord",
                platform_user_id=user_info["id"],
                username=user_info.get("username")
            )
            user_id = user['id']
        else:
            user = storage.create_user()
            user_id = user['id']
            storage.bind_platform(
                user_id=user_id,
                platform="discord",
                platform_user_id=user_info["id"],
                username=user_info.get("username")
            )
    except ValueError as e:
        return RedirectResponse(f"/?error={str(e)}", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/?error=Failed to save account data. Please try again.", status_code=303)

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=/dashboard">
        <title>Redirecting...</title>
    </head>
    <body>
        <p>Authentication successful! Redirecting to dashboard...</p>
        <script>
            setTimeout(function() {
                window.location.href = '/dashboard';
            }, 100);
        </script>
    </body>
    </html>
    """
    html_response = HTMLResponse(content=html_content, status_code=200)
    session_manager.set_session_cookie(html_response, user_id)

    return html_response


@router.get("/me")
async def get_current_user(user_id: int = Depends(get_current_user_id)):
    storage = get_user_storage()
    user = storage.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    bindings = {}
    for platform in ['discord', 'telegram']:
        platform_data = user.get(platform)
        if platform_data and platform_data.get('bound'):
            bindings[platform] = {
                "username": platform_data.get('username'),
                "platform_user_id": platform_data.get('id'),
                "bound": True
            }

    discord_bound = 'discord' in bindings
    telegram_bound = 'telegram' in bindings

    return {
        "user_id": user['id'],
        "bindings": bindings,
        "is_complete": discord_bound and telegram_bound,
        "all_platforms_bound": len(bindings) == 2
    }


@router.get("/telegram")
async def telegram_auth(user_id: int = Depends(get_current_user_id)):
    auth_code = telegram_authz.generate_auth_code(str(user_id))
    if auth_code in telegram_authz.pending_auth_codes:
        telegram_authz.pending_auth_codes[auth_code]["user_id"] = user_id
    auth_url = telegram_authz.get_authorization_url(auth_code)
    return {"auth_url": auth_url, "expires_in": 900}


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        result = await handle_update(update)
        return result
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/logout")
async def logout(response: Response):
    session_manager.clear_session_cookie(response)
    return {"message": "Logged out successfully"}
