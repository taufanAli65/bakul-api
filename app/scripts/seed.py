from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.domain.users.repositories import UserRepository
from app.domain.users.schemas import UserCreate, UserRole
from app.domain.auth.security import get_password_hash
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_admin():
    async with SessionLocal() as db:
        try:
            user_repo = UserRepository(db)
            existing_admin = await user_repo.get_user_by_email("admin@admin.com")
            if not existing_admin:
                logger.info("Creating admin user...")
                admin_in = UserCreate(
                    name="Admin User",
                    email="admin@admin.com",
                    password="adminpassword",
                    role=UserRole.ADMIN,
                    profile_picture=None
                )
                hashed_password = get_password_hash(admin_in.password)
                await user_repo.create_user(admin_in, hashed_password)
                logger.info("Admin user created successfully.")
            else:
                logger.info("Admin user already exists.")
        except Exception as e:
            logger.error(f"Error seeding admin: {e}")

if __name__ == "__main__":
    asyncio.run(seed_admin())
