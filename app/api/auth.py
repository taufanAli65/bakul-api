from fastapi import APIRouter, Depends, status
from app.domain.users.schemas import UserLogin, UserCreate
from app.domain.users.service import UserService
from app.core.dependencies import get_auth_service, get_user_service
from app.domain.auth.service import AuthService
from app.utils.response_utils import create_response

router = APIRouter()

@router.post("/login", response_model=None)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate_user(login_data)
    if not user:
        return create_response(
            success=False,
            message="Incorrect email or password",
            error_code="INVALID_CREDENTIALS",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    access_token = auth_service.create_token(user.id_user)
    return create_response(
        success=True,
        message="Login successful",
        data={
            "access_token": access_token, 
            "token_type": "bearer"
        }
    )

@router.post("/register", response_model=None)
async def register(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    existing_user = await user_service.get_user_by_email(user_in.email)
    if existing_user:
        return create_response(
            success=False,
            message="User with this email already exists",
            error_code="USER_EXISTS",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    user_in.role = UserRole.USER
    user = await user_service.create_user(user_in)
    return create_response(
        success=True,
        message="User created successfully",
        data={
            "id": str(user.id_user),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "profile_picture": user.profile_picture
        },
        status_code=status.HTTP_201_CREATED
    )
