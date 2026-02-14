import uuid
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.users.models import MstUser, UserRole
from app.domain.users.schemas import UserCreate, UserUpdate
from typing import Optional

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[MstUser]:
        result = await self.db.execute(select(MstUser).where(MstUser.email == email))
        return result.scalars().first()

    async def create_user(self, user_in: UserCreate, hashed_password: str) -> MstUser:
        new_user = MstUser(
            name=user_in.name,
            email=user_in.email,
            role=user_in.role,
            profile_picture=user_in.profile_picture,
            password=hashed_password
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update_user(self, user_id: uuid.UUID, user_in: UserUpdate) -> Optional[MstUser]:
        result = await self.db.execute(select(MstUser).where(MstUser.id_user == user_id))
        user = result.scalars().first()
        if not user:
            return None
        
        update_data = user_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

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