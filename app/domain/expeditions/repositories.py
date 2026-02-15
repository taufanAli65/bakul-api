import uuid
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.expeditions.models import MstExpeditionService
from typing import Optional

class ExpeditionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_expedition_service(self, name: str) -> MstExpeditionService:
        new_service = MstExpeditionService(name=name)
        self.db.add(new_service)
        await self.db.commit()
        await self.db.refresh(new_service)
        return new_service
    
    async def bulk_create_expedition_services(self, services: list[str]) -> list[MstExpeditionService]:
        new_services = [MstExpeditionService(name=name) for name in services]
        self.db.add_all(new_services)
        await self.db.commit()
        for service in new_services:
            await self.db.refresh(service)
        return new_services

    async def update_expedition_service(self, service_id: uuid.UUID, name: str) -> Optional[MstExpeditionService]:
        result = await self.db.execute(select(MstExpeditionService).where(MstExpeditionService.id_expedition_service == service_id))
        service = result.scalars().first()
        if not service:
            return None
        
        service.name = name
        self.db.add(service)
        await self.db.commit()
        await self.db.refresh(service)
        return service
        
    async def get_expedition_service_by_id(self, service_id: uuid.UUID) -> Optional[MstExpeditionService]:
        result = await self.db.execute(select(MstExpeditionService).where(MstExpeditionService.id_expedition_service == service_id))
        return result.scalars().first()
    
    async def get_all_expedition_services(self, limit: int = 10, offset: int = 0) -> list[MstExpeditionService]:
        result = await self.db.execute(select(MstExpeditionService).limit(limit).offset(offset))
        return result.scalars().all()

    async def delete_expedition_service(self, service_id: uuid.UUID) -> bool:
        result = await self.db.execute(select(MstExpeditionService).where(MstExpeditionService.id_expedition_service == service_id))
        service = result.scalars().first()
        if not service:
            return False
        await self.db.delete(service)
        await self.db.commit()
        return True