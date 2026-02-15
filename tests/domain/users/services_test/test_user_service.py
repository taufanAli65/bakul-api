import pytest

from app.domain.users.models import UserRole
from app.domain.users.repositories import UserRepository
from app.domain.users.schemas import UserCreate, UserUpdate
from app.domain.users.service import UserService


@pytest.mark.asyncio
async def test_create_user_hashes_password(db_session):
    repo = UserRepository(db_session)
    service = UserService(repo)

    user = await service.create_user(
        UserCreate(
            name="Service User",
            email="service@example.com",
            role=UserRole.USER,
            profile_picture=None,
            password="plainpass",
        )
    )

    assert user is not None
    assert user.password != "plainpass"


@pytest.mark.asyncio
async def test_update_user_changes_fields(db_session, user_factory):
    repo = UserRepository(db_session)
    service = UserService(repo)
    user = await service.create_user(
        UserCreate(
            name="Old",
            email="old@example.com",
            role=UserRole.USER,
            profile_picture=None,
            password="secret",
        )
    )

    updated = await service.update_user(
        user.id_user,
        UserUpdate(name="New", email="new@example.com", role=UserRole.ADMIN, profile_picture="pic"),
    )

    assert updated is not None
    assert updated.name == "New"
    assert updated.email == "new@example.com"
    assert updated.role == UserRole.ADMIN
