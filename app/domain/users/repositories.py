import uuid
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.users.models import MstUser, UserRole
from typing import Optional

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[MstUser]:
        result = await self.db.execute(select(MstUser).where(MstUser.email == email))
        return result.scalars().first()

    async def create_user(
        self,
        *,
        name: str,
        email: str,
        role: UserRole,
        profile_picture: Optional[str],
        hashed_password: str,
    ) -> MstUser:
        new_user = MstUser(
            name=name,
            email=email,
            role=role,
            profile_picture=profile_picture,
            password=hashed_password,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update_user(
        self,
        user_id: uuid.UUID,
        *,
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[UserRole] = None,
        profile_picture: Optional[str] = None,
    ) -> Optional[MstUser]:
        result = await self.db.execute(select(MstUser).where(MstUser.id_user == user_id))
        user = result.scalars().first()
        if not user:
            return None
        
        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if role is not None:
            user.role = role
        if profile_picture is not None:
            user.profile_picture = profile_picture

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[MstUser]:
        result = await self.db.execute(select(MstUser).where(MstUser.id_user == user_id))
        return result.scalars().first()

    async def get_all_users(self, limit: int = 10, offset: int = 0) -> list[MstUser]:
        result = await self.db.execute(select(MstUser).limit(limit).offset(offset))
        return result.scalars().all()