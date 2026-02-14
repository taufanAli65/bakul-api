from fastapi import APIRouter, Depends, status
from app.domain.users.schemas import UserUpdate, UserRole
from app.core.dependencies import get_user_service, get_current_user, get_current_admin
from app.domain.users.service import UserService
from app.domain.users.models import MstUser
from app.utils.response_utils import create_response

router = APIRouter()

@router.get("/me", response_model=None)
async def read_users_me(
    current_user: MstUser = Depends(get_current_user)
):
    return create_response(
        success=True,
        message="User profile retrieved successfully",
        data={
            "id": str(current_user.id_user),
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
            "profile_picture": current_user.profile_picture
        }
    )

@router.put("/me", response_model=None)
async def update_user_me(
    user_in: UserUpdate,
    current_user: MstUser = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):

    user = await user_service.update_user(current_user.id_user, user_in)
    return create_response(
        success=True,
        message="User profile updated successfully",
        data={
            "id": str(user.id_user),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "profile_picture": user.profile_picture
        }
    )

@router.get("/", response_model=None)
async def read_users(
    current_user: MstUser = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
    limit: int = 10,
    offset: int = 0
):
    users = await user_service.get_all_users(limit, offset)
    return create_response(
        success=True,
        message="Users retrieved successfully",
        data=[
            {
                "id": str(user.id_user),
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "profile_picture": user.profile_picture
            }
            for user in users
        ],
        pagination={
            "limit": limit,
            "offset": offset,
            "total": len(users)
        }
    )