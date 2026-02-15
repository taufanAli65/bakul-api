from app.domain.users.repositories import UserRepository
from app.domain.users.schemas import UserUpdate, UserBase, UserCreate
from typing import Optional
from app.domain.users.models import MstUser, UserRole
from app.domain.auth.security import get_password_hash

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_email(self, email: str) -> Optional[UserBase]:
        return await self.user_repo.get_user_by_email(email)
    
    async def create_user(self, user_in: UserCreate) -> MstUser:
        hashed_password = get_password_hash(user_in.password)
        role = user_in.role if isinstance(user_in.role, UserRole) else UserRole(user_in.role)
        return await self.user_repo.create_user(
            name=user_in.name,
            email=user_in.email,
            role=role,
            profile_picture=user_in.profile_picture,
            hashed_password=hashed_password,
        )

    async def update_user(self, user_id: str, user_in: UserUpdate) -> Optional[UserBase]:
        role = None
        if user_in.role is not None:
            role = user_in.role if isinstance(user_in.role, UserRole) else UserRole(user_in.role)

        return await self.user_repo.update_user(
            user_id,
            name=user_in.name,
            email=user_in.email,
            role=role,
            profile_picture=user_in.profile_picture,
        )

    async def get_user_by_id(self, user_id: str) -> Optional[UserBase]:
        return await self.user_repo.get_user_by_id(user_id)
    
    async def get_all_users(self, limit: int = 10, offset: int = 0) -> list[MstUser]:
        return await self.user_repo.get_all_users(limit, offset)
    