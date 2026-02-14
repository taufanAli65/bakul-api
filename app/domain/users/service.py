from app.domain.users.repositories import UserRepository
from app.domain.users.schemas import UserUpdate, UserBase, UserCreate
from typing import Optional
from app.domain.users.models import MstUser
from app.domain.auth.security import get_password_hash

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_email(self, email: str) -> Optional[UserBase]:
        return await self.user_repo.get_user_by_email(email)
    
    async def create_user(self, user_in: UserCreate) -> MstUser:
        hashed_password = get_password_hash(user_in.password)
        return await self.user_repo.create_user(user_in, hashed_password)

    async def update_user(self, user_id: str, user_in: UserUpdate) -> Optional[UserBase]:
        return await self.user_repo.update_user(user_id, user_in)

    async def get_user_by_id(self, user_id: str) -> Optional[UserBase]:
        return await self.user_repo.get_user_by_id(user_id)
    
    async def get_all_users(self, limit: int = 10, offset: int = 0) -> list[MstUser]:
        return await self.user_repo.get_all_users(limit, offset)
    