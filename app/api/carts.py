import uuid
from fastapi import APIRouter, Depends, status
from app.domain.users.schemas import UserRole
from app.domain.users.models import MstUser
from app.core.dependencies import get_user_service, get_current_admin, get_current_user, get_cart_service, get_product_service
from app.utils.response_utils import create_response
from app.domain.carts.services import CartService
from app.domain.products.services import ProductService
from app.domain.carts.schemas import CartCreate, CartDelete, CartUpdate

router = APIRouter()

@router.post("/", response_model=None)
async def create_cart(
    product_id: uuid.UUID,
    quantity: int,
    cart_service: CartService = Depends(get_cart_service),
    product_service: ProductService = Depends(get_product_service),
    current_user: MstUser = Depends(get_current_user)
):
    user_id = current_user.id_user
    product = await product_service.get_product_by_id(product_id)
    if not product:
        return create_response(
            success=False,
            message="Product not found",
            error_code="PRODUCT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    if product.stock < quantity:
        return create_response(
            success=False,
            message="Insufficient stock for the product",
            error_code="INSUFFICIENT_STOCK",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    cart_in = CartCreate(
        id_user=user_id,
        id_product=product_id,
        quantity=quantity,
        price_at_time=product.price * quantity,
    )
    new_cart = await cart_service.create_cart(cart_in)
    return create_response(
        success=True,
        message="Cart item created successfully",
        data={
            "id": str(new_cart.id_cart),
            "user_id": str(new_cart.id_user),
            "product_id": str(new_cart.id_product),
            "quantity": new_cart.quantity,
            "price_at_time": new_cart.price_at_time
        },
        status_code=status.HTTP_201_CREATED
    )

@router.get("/user/{user_id}", response_model=None)
async def read_carts_by_user_id_admin_only(
    user_id: uuid.UUID,
    cart_service: CartService = Depends(get_cart_service),
    current_user: MstUser = Depends(get_current_admin),
    limit: int = 10,
    offset: int = 0
):
    carts = await cart_service.get_carts_by_user_id(user_id, limit, offset)
    return create_response(
        success=True,
        message="Cart items retrieved successfully",
        data=[
            {
                "id": str(cart.id_cart),
                "user_id": str(cart.id_user),
                "product_id": str(cart.id_product),
                "quantity": cart.quantity,
                "price_at_time": cart.price_at_time
            }
            for cart in carts
        ],
        status_code=status.HTTP_200_OK,
        pagination={
            "limit": limit,
            "offset": offset,
            "total": len(carts)
        }
    )

@router.get("/", response_model=None)
async def read_carts_by_user_id(
    cart_service: CartService = Depends(get_cart_service),
    current_user: MstUser = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    user_id = current_user.id_user
    carts = await cart_service.get_carts_by_user_id(user_id, limit, offset)
    return create_response(
        success=True,
        message="Cart items retrieved successfully",
        data=[
            {
                "id": str(cart.id_cart),
                "user_id": str(cart.id_user),
                "product_id": str(cart.id_product),
                "quantity": cart.quantity,
                "price_at_time": cart.price_at_time
            }
            for cart in carts
        ],
        status_code=status.HTTP_200_OK,
        pagination={
            "limit": limit,
            "offset": offset,
            "total": len(carts)
        }
    )

@router.delete("/item", response_model=None)
async def delete_cart_item(
    product_id: uuid.UUID,
    cart_service: CartService = Depends(get_cart_service),
    current_user: MstUser = Depends(get_current_user)
):
    user_id = current_user.id_user
    cart_in = CartDelete(id_user=user_id, id_product=product_id)
    success = await cart_service.delete_cart_each_item(cart_in)
    if not success:
        return create_response(
            success=False,
            message="Cart item not found",
            error_code="CART_ITEM_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return create_response(
        success=True,
        message="Cart item deleted successfully",
        status_code=status.HTTP_200_OK
    )

@router.delete("/empty", response_model=None)
async def empty_cart(
    cart_service: CartService = Depends(get_cart_service),
    current_user: MstUser = Depends(get_current_user)
):
    user_id = current_user.id_user
    success = await cart_service.empty_cart_by_user_id(user_id)
    if not success:
        return create_response(
            success=False,
            message="No cart items found for the user",
            error_code="CART_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return create_response(
        success=True,
        message="Cart emptied successfully",
        status_code=status.HTTP_200_OK
    )

@router.put("/{cart_id}", response_model=None)
async def update_cart_item(
    cart_id: uuid.UUID,
    quantity: int,
    cart_service: CartService = Depends(get_cart_service),
    product_service: ProductService = Depends(get_product_service),
    current_user: MstUser = Depends(get_current_user)
):
    cart = await cart_service.get_cart_by_id(cart_id)
    if not cart:
        return create_response(
            success=False,
            message="Cart item not found",
            error_code="CART_ITEM_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    if cart.id_user != current_user.id_user:
        return create_response(
            success=False,
            message="Unauthorized to update this cart item",
            error_code="UNAUTHORIZED",
            status_code=status.HTTP_403_FORBIDDEN
        )
    product = await product_service.get_product_by_id(cart.id_product)
    if not product:
        return create_response(
            success=False,
            message="Product not found",
            error_code="PRODUCT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if product.stock < quantity:
        return create_response(
            success=False,
            message="Insufficient stock for the product",
            error_code="INSUFFICIENT_STOCK",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    cart_in = CartUpdate(quantity=quantity, price_at_time=product.price * quantity)
    updated_cart = await cart_service.update_cart(cart_id, cart_in)
    return create_response(
        success=True,
        message="Cart item updated successfully",
        data={
            "id": str(updated_cart.id_cart),
            "user_id": str(updated_cart.id_user),
            "product_id": str(updated_cart.id_product),
            "quantity": updated_cart.quantity,
            "price_at_time": updated_cart.price_at_time
        },
        status_code=status.HTTP_200_OK
    )