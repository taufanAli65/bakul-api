from app.domain.users.repositories import UserRepository
from app.domain.auth.security import verify_password, create_access_token
from app.domain.users.schemas import UserLogin
from typing import Optional
from datetime import timedelta
from app.core.config import settings

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate_user(self, login_data: UserLogin) -> Optional[dict]:
        user = await self.user_repo.get_user_by_email(login_data.email)
        if not user:
            return None
        if not verify_password(login_data.password, user.password):
            return None
        return user

    def create_token(self, user_id: str) -> str:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        return create_access_token(subject=user_id, expires_delta=access_token_expires)
