from fastapi import Depends, HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.domain.auth.security import ALGORITHM
from app.domain.auth.schemas import TokenData
from app.domain.users.repositories import UserRepository
from app.domain.users.service import UserService
from app.domain.users.models import MstUser
from app.domain.auth.service import AuthService
from app.domain.products.repositories import ProductRepository
from app.domain.products.services import ProductService
from app.domain.expeditions.repositories import ExpeditionRepository
from app.domain.expeditions.services import ExpeditionService
from app.domain.carts.repositories import CartRepository
from app.domain.carts.services import CartService
from app.domain.transactions.repositories import TransactionRepository
from app.domain.transactions.services import TransactionService

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

# Repositories
def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_product_repo(db: AsyncSession = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)

def get_expedition_repo(db: AsyncSession = Depends(get_db)) -> ExpeditionRepository:
    return ExpeditionRepository(db)

def get_cart_repo(db: AsyncSession = Depends(get_db)) -> CartRepository:
    return CartRepository(db)

def get_transaction_repo(db: AsyncSession = Depends(get_db)) -> TransactionRepository:
    return TransactionRepository(db)

# Services
def get_user_service(user_repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)

def get_product_service(product_repo: ProductRepository = Depends(get_product_repo)) -> ProductService:
    return ProductService(product_repo)

def get_expedition_service(expedition_repo: ExpeditionRepository = Depends(get_expedition_repo)) -> ExpeditionService:
    return ExpeditionService(expedition_repo)

def get_cart_service(cart_repo: CartRepository = Depends(get_cart_repo)) -> CartService:
    return CartService(cart_repo)

def get_transaction_service(
    transaction_repo: TransactionRepository = Depends(get_transaction_repo),
    expedition_repo: ExpeditionRepository = Depends(get_expedition_repo),
    product_repo: ProductRepository = Depends(get_product_repo),
    cart_repo: CartRepository = Depends(get_cart_repo),
) -> TransactionService:
    return TransactionService(transaction_repo, expedition_repo, product_repo, cart_repo)

def get_auth_service(user_repo: UserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo)

# Auth Dependency
async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> MstUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, settings.secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: MstUser = Depends(get_current_user)) -> MstUser:
    if current_user.role != "admin":
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
