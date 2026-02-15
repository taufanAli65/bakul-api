import pytest

from app.domain.expeditions.repositories import ExpeditionRepository
from app.domain.expeditions.services import ExpeditionService


@pytest.mark.asyncio
async def test_expedition_service_crud(db_session):
    repo = ExpeditionRepository(db_session)
    service = ExpeditionService(repo)

    created = await service.create_expedition_service("Prime")
    assert created.name == "Prime"

    listed = await service.get_all_expedition_services(limit=10, offset=0)
    assert len(listed) == 1

    updated = await service.update_expedition_service(created.id_expedition_service, "Prime+")
    assert updated is not None
    assert updated.name == "Prime+"
