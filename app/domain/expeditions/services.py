from app.domain.expeditions.repositories import ExpeditionRepository
from app.domain.expeditions.models import MstExpeditionService
from typing import Optional

class ExpeditionService:
    def __init__(self, expedition_repo: ExpeditionRepository):
        self.expedition_repo = expedition_repo

    async def create_expedition_service(self, name: str) -> MstExpeditionService:
        return await self.expedition_repo.create_expedition_service(name)

    async def bulk_create_expedition_services(self, services: list[str]) -> list[MstExpeditionService]:
        return await self.expedition_repo.bulk_create_expedition_services(services)

    async def update_expedition_service(self, service_id: str, name: str) -> Optional[MstExpeditionService]:
        return await self.expedition_repo.update_expedition_service(service_id, name)

    async def get_expedition_service_by_id(self, service_id: str) -> Optional[MstExpeditionService]:
        return await self.expedition_repo.get_expedition_service_by_id(service_id)
    
    async def get_all_expedition_services(self, limit: int = 10, offset: int = 0) -> list[MstExpeditionService]:
        return await self.expedition_repo.get_all_expedition_services(limit, offset)