from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from db import get_db
from middleware.auth_middleware import get_current_user, get_current_admin_user
from services.product_service import ProductService


router = APIRouter(prefix="/api/products", tags=["products"])
product_service = ProductService()


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    article: str = Field(min_length=1, max_length=10)
    description: Optional[str] = None
    price: float
    product_type: str = Field(min_length=1, max_length=30)
    stock: int = 0
    rating: float = 0.0
    image_url: Optional[str] = None


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    article: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    product_type: Optional[str] = None
    stock: Optional[int] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None


@router.get("")
def get_products(
    product_type: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    is_new: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    result, status_code = product_service.get_products(
        db=db,
        product_type=product_type,
        search=search,
        is_new=is_new,
        skip=skip,
        limit=limit
    )
    return JSONResponse(status_code=status_code, content=result)


@router.post("")
def create_product(
    data: ProductCreateRequest,
    current_admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    result, status_code = product_service.create_product(
        db=db,
        name=data.name,
        article=data.article,
        description=data.description,
        price=data.price,
        product_type=data.product_type,
        stock=data.stock,
        rating=data.rating,
        image_url=data.image_url
    )

    return JSONResponse(
        status_code=status_code,
        content=result
    )


@router.put("/{product_id}")
def update_product(
    product_id: int,
    data: ProductUpdateRequest,
    current_admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    result, status_code = product_service.update_product(
        db=db,
        product_id=product_id,
        name=data.name,
        article=data.article,
        description=data.description,
        price=data.price,
        product_type=data.product_type,
        stock=data.stock,
        rating=data.rating,
        image_url=data.image_url
    )

    return JSONResponse(
        status_code=status_code,
        content=result
    )


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    result, status_code = product_service.delete_product(
        db=db,
        product_id=product_id
    )

    return JSONResponse(
        status_code=status_code,
        content=result
    )


@router.post("/import")
def import_products(
    current_admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    result, status_code = product_service.import_from_json(db=db)
    return JSONResponse(status_code=status_code, content=result)