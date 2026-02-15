import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from app.domain.products.schemas import ProductCreate, ProductUpdate
from app.domain.users.models import MstUser
from app.core.dependencies import get_current_admin, get_product_service
from app.domain.products.services import ProductService
from app.utils.response_utils import create_response
from app.core.image_service import ImageService

router = APIRouter()

@router.get("/", response_model=None)
async def read_products(
    product_service: ProductService = Depends(get_product_service),
    limit: int = 10,
    offset: int = 0
):
    products = await product_service.get_all_products(limit, offset)
    return create_response(
        success=True,
        message="Products retrieved successfully",
        data=[
            {
                "id": str(product.id_product),
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": getattr(product, "stock", None),
                "image_url": product.product_image_url
            }
            for product in products
        ],
        status_code=status.HTTP_200_OK,
        pagination={
            "limit": limit,
            "offset": offset,
            "total": len(products)
        }
    )

@router.get("/{product_id}", response_model=None)
async def read_product(
    product_id: uuid.UUID,
    product_service: ProductService = Depends(get_product_service)
):
    product = await product_service.get_product_by_id(product_id)
    if not product:
        return create_response(
            success=False,
            message="Product not found",
            error_code="PRODUCT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return create_response(
        success=True,
        message="Product retrieved successfully",
        data={
            "id": str(product.id_product),
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": getattr(product, "stock", None),
            "image_url": product.product_image_url
        },
        status_code=status.HTTP_200_OK
    )

@router.post("/", response_model=None)
async def create_product(
    name: str = Form(...),
    price: int = Form(...),
    stock: int = Form(...),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: MstUser = Depends(get_current_admin),
    product_service: ProductService = Depends(get_product_service),
    image_service: ImageService = Depends()
):
    image_url = None
    if image:
        image_url = await image_service.upload_image(image)

    product_in = ProductCreate(
        name=name,
        description=description,
        price=price,
        stock=stock,
        product_image_url=image_url,
    )

    product = await product_service.create_product(product_in)
    return create_response(
        success=True,
        message="Product created successfully",
        data={
            "id": str(product.id_product),
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": getattr(product, "stock", None),
            "image_url": product.product_image_url
        },
        status_code=status.HTTP_201_CREATED
    )

@router.put("/{product_id}", response_model=None)
async def update_product(
    product_id: uuid.UUID,
    product_in: ProductUpdate,
    current_user: MstUser = Depends(get_current_admin),
    product_service: ProductService = Depends(get_product_service)
):
    product = await product_service.update_product(product_id, product_in)
    if not product:
        return create_response(
            success=False,
            message="Product not found",
            error_code="PRODUCT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return create_response(
        success=True,
        message="Product updated successfully",
        data={
            "id": str(product.id_product),
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": getattr(product, "stock", None),
            "image_url": product.product_image_url
        },
        status_code=status.HTTP_200_OK
    )

@router.put("/{product_id}/stock", response_model=None)
async def update_product_stock(
    product_id: uuid.UUID,
    stock: int,
    current_user: MstUser = Depends(get_current_admin),
    product_service: ProductService = Depends(get_product_service)
):
    product_stock = await product_service.update_product_stock(product_id, stock)
    if not product_stock:
        return create_response(
            success=False,
            message="Product not found",
            error_code="PRODUCT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return create_response(
        success=True,
        message="Product stock updated successfully",
        data={
            "id": str(product_stock.id_product),
            "stock": product_stock.stock
        },
        status_code=status.HTTP_200_OK
    )

@router.delete("/{product_id}", response_model=None)
async def delete_product(
    product_id: uuid.UUID,
    current_user: MstUser = Depends(get_current_admin),
    product_service: ProductService = Depends(get_product_service),
    image_service: ImageService = Depends()
):
    product = await product_service.get_product_by_id(product_id)
    if not product:
        return create_response(
            success=False,
            message="Product not found",
            error_code="PRODUCT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    if product.product_image_url:
        image_service.delete_image(product.product_image_url)

    success = await product_service.delete_product(product_id)
    return create_response(
        success=True,
        message="Product deleted successfully",
        status_code=status.HTTP_200_OK
    )