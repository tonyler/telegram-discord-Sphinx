from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Cookie, HTTPException, Response
from typing import Optional
from app.config import get_settings

settings = get_settings()


class SessionManager:
    def __init__(self):
        self.serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        self.cookie_name = "session"
        self.max_age = 86400 * 7

    def create_session(self, user_id: int) -> str:
        return self.serializer.dumps({"user_id": user_id})

    def get_user_id(self, session_token: Optional[str]) -> Optional[int]:
        if not session_token:
            return None

        try:
            data = self.serializer.loads(session_token, max_age=self.max_age)
            return data.get("user_id")
        except (BadSignature, SignatureExpired):
            return None

    def set_session_cookie(self, response: Response, user_id: int):
        session_token = self.create_session(user_id)
        is_production = settings.ENVIRONMENT == "production"
        response.set_cookie(
            key=self.cookie_name,
            value=session_token,
            max_age=self.max_age,
            httponly=True,
            secure=is_production,
            samesite="lax",
            path="/"
        )

    def clear_session_cookie(self, response: Response):
        response.delete_cookie(key=self.cookie_name)


session_manager = SessionManager()


def get_current_user_id(session: Optional[str] = Cookie(None, alias="session")) -> int:
    user_id = session_manager.get_user_id(session)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


def get_optional_user_id(session: Optional[str] = Cookie(None, alias="session")) -> Optional[int]:
    return session_manager.get_user_id(session)
