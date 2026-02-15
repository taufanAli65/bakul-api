import pytest

from app.domain.users.models import UserRole
from app.domain.users.repositories import UserRepository
from app.domain.auth.security import get_password_hash


@pytest.mark.asyncio
async def test_create_and_get_user(db_session):
    repo = UserRepository(db_session)
    user = await repo.create_user(
        name="Test User",
        email="repo-user@example.com",
        role=UserRole.USER,
        profile_picture=None,
        hashed_password=get_password_hash("password"),
    )

    fetched_by_email = await repo.get_user_by_email("repo-user@example.com")
    fetched_by_id = await repo.get_user_by_id(user.id_user)

    assert fetched_by_email is not None
    assert fetched_by_id is not None
    assert fetched_by_email.id_user == user.id_user


@pytest.mark.asyncio
async def test_update_user(db_session):
    repo = UserRepository(db_session)
    user = await repo.create_user(
        name="Old Name",
        email="old@example.com",
        role=UserRole.USER,
        profile_picture=None,
        hashed_password=get_password_hash("password"),
    )

    updated = await repo.update_user(
        user.id_user,
        name="New Name",
        email="new@example.com",
        role=UserRole.ADMIN,
        profile_picture="pic.png",
    )

    assert updated is not None
    assert updated.name == "New Name"
    assert updated.email == "new@example.com"
    assert updated.role == UserRole.ADMIN
    assert updated.profile_picture == "pic.png"

    all_users = await repo.get_all_users(limit=10, offset=0)
    assert len(all_users) == 1
    assert all_users[0].name == "New Name"
