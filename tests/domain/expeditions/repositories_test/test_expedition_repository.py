import pytest
from app.domain.expeditions.repositories import ExpeditionRepository


@pytest.mark.asyncio
async def test_create_and_list_expedition_services(db_session):
    repo = ExpeditionRepository(db_session)
    service = await repo.create_expedition_service("FastShip")
    bulk = await repo.bulk_create_expedition_services(["Regular", "Express"])

    services = await repo.get_all_expedition_services(limit=10, offset=0)
    names = {svc.name for svc in services}

    assert service.name in names
    assert {"Regular", "Express"}.issubset(names)


@pytest.mark.asyncio
async def test_update_and_delete_expedition_service(db_session):
    repo = ExpeditionRepository(db_session)
    service = await repo.create_expedition_service("OldName")

    updated = await repo.update_expedition_service(service.id_expedition_service, "NewName")
    assert updated is not None
    assert updated.name == "NewName"

    deleted = await repo.delete_expedition_service(service.id_expedition_service)
    assert deleted is True

    missing = await repo.get_expedition_service_by_id(service.id_expedition_service)
    assert missing is None
