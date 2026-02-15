import pytest

from app.domain.auth.service import AuthService
from app.domain.auth.security import get_password_hash
from app.domain.users.repositories import UserRepository
from app.domain.users.schemas import UserLogin
from app.domain.users.models import UserRole


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session):
    repo = UserRepository(db_session)
    await repo.create_user(
        name="Auth User",
        email="auth@example.com",
        role=UserRole.USER,
        profile_picture=None,
        hashed_password=get_password_hash("secret"),
    )

    service = AuthService(repo)
    user = await service.authenticate_user(UserLogin(email="auth@example.com", password="secret"))

    assert user is not None
    assert user.email == "auth@example.com"


@pytest.mark.asyncio
async def test_authenticate_user_failure(db_session):
    repo = UserRepository(db_session)
    service = AuthService(repo)

    user = await service.authenticate_user(UserLogin(email="missing@example.com", password="bad"))
    assert user is None


@pytest.mark.asyncio
async def test_create_token(db_session, user_factory):
    user = await user_factory(email="token@example.com")
    repo = UserRepository(db_session)
    service = AuthService(repo)

    token = service.create_token(str(user.id_user))
    assert isinstance(token, str)
    assert token
