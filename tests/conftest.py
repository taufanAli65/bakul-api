import os
import sys
import uuid
from typing import Optional
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is on the Python path so 'app' imports resolve when tests are run
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.core.base_class import Base
from app.core.dependencies import get_current_admin, get_current_user, get_db
from app.domain.auth.security import get_password_hash
from app.domain.carts.models import MstCart
from app.domain.expeditions.models import MstExpeditionService
from app.domain.products.models import MstProduct, TrnProductStock
from app.domain.transactions.models import MstTransaction, TrnTransactionItem, TrnTransactionStatus
from app.domain.users.models import MstUser, UserRole
from app.domain.users.repositories import UserRepository
from app.main import app as fastapi_app

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        DATABASE_URL,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def user_factory(db_session: AsyncSession):
    async def _create_user(*, role: UserRole = UserRole.USER, email: Optional[str] = None, password: str = "password123") -> MstUser:
        repo = UserRepository(db_session)
        return await repo.create_user(
            name=f"user-{uuid.uuid4().hex[:6]}",
            email=email or f"user-{uuid.uuid4().hex[:6]}@example.com",
            role=role,
            profile_picture=None,
            hashed_password=get_password_hash(password),
        )

    return _create_user


@pytest_asyncio.fixture
async def admin_user(user_factory):
    return await user_factory(role=UserRole.ADMIN, email="admin@example.com")


@pytest_asyncio.fixture
async def regular_user(user_factory):
    return await user_factory(role=UserRole.USER, email="user@example.com")


@pytest_asyncio.fixture
async def app(db_session: AsyncSession, regular_user: MstUser, admin_user: MstUser):
    async def override_get_db():
        yield db_session

    async def override_get_current_user():
        return regular_user

    async def override_get_current_admin():
        return admin_user

    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.dependency_overrides[get_current_user] = override_get_current_user
    fastapi_app.dependency_overrides[get_current_admin] = override_get_current_admin

    yield fastapi_app

    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        yield client
