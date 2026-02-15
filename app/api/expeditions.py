import uuid
from fastapi import APIRouter, Depends, status
from app.domain.users.schemas import UserRole
from app.domain.users.models import MstUser
from app.core.dependencies import get_user_service, get_current_admin
from app.utils.response_utils import create_response
from app.domain.expeditions.services import ExpeditionService

router = APIRouter()

@router.post("/", response_model=None)
async def create_expedition_service(
    name: str,
    expedition_service: ExpeditionService = Depends(get_user_service),
    current_user: MstUser = Depends(get_current_admin)
):
    new_service = await expedition_service.create_expedition_service(name)
    return create_response(
        success=True,
        message="Expedition service created successfully",
        data={
            "id": str(new_service.id_expedition_service),
            "name": new_service.name
        },
        status_code=status.HTTP_201_CREATED
    )

@router.post("/bulk", response_model=None)
async def bulk_create_expedition_services(
    services: list[str],
    expedition_service: ExpeditionService = Depends(get_user_service),
    current_user: MstUser = Depends(get_current_admin)
):
    new_services = await expedition_service.bulk_create_expedition_services(services)
    return create_response(
        success=True,
        message="Expedition services created successfully",
        data=[
            {
                "id": str(service.id_expedition_service),
                "name": service.name
            }
            for service in new_services
        ],
        status_code=status.HTTP_201_CREATED
    )

@router.get("/", response_model=None)
async def read_expedition_services(
    expedition_service: ExpeditionService = Depends(get_user_service),
    limit: int = 10,
    offset: int = 0
):
    services = await expedition_service.get_all_expedition_services(limit, offset)
    return create_response(
        success=True,
        message="Expedition services retrieved successfully",
        data=[
            {
                "id": str(service.id_expedition_service),
                "name": service.name
            }
            for service in services
        ],
        status_code=status.HTTP_200_OK,
        pagination={
            "limit": limit,
            "offset": offset,
            "total": len(services)
        }
    )

@router.get("/{service_id}", response_model=None)
async def read_expedition_service(
    service_id: uuid.UUID,
    expedition_service: ExpeditionService = Depends(get_user_service)
):
    service = await expedition_service.get_expedition_service_by_id(service_id)
    if not service:
        return create_response(
            success=False,
            message="Expedition service not found",
            error_code="EXPEDITION_SERVICE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return create_response(
        success=True,
        message="Expedition service retrieved successfully",
        data={
            "id": str(service.id_expedition_service),
            "name": service.name
        },
        status_code=status.HTTP_200_OK
    )

@router.put("/{service_id}", response_model=None)
async def update_expedition_service(
    service_id: uuid.UUID,
    name: str,
    expedition_service: ExpeditionService = Depends(get_user_service),
    current_user: MstUser = Depends(get_current_admin)
):
    updated_service = await expedition_service.update_expedition_service(service_id, name)
    if not updated_service:
        return create_response(
            success=False,
            message="Expedition service not found",
            error_code="EXPEDITION_SERVICE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return create_response(
        success=True,
        message="Expedition service updated successfully",
        data={
            "id": str(updated_service.id_expedition_service),
            "name": updated_service.name
        },
        status_code=status.HTTP_200_OK
    )

@router.delete("/{service_id}", response_model=None)
async def delete_expedition_service(
    service_id: uuid.UUID,
    expedition_service: ExpeditionService = Depends(get_user_service),
    current_user: MstUser = Depends(get_current_admin)
):
    deleted = await expedition_service.delete_expedition_service(service_id)
    if not deleted:
        return create_response(
            success=False,
            message="Expedition service not found",
            error_code="EXPEDITION_SERVICE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return create_response(
        success=True,
        message="Expedition service deleted successfully",
        status_code=status.HTTP_200_OK
    )