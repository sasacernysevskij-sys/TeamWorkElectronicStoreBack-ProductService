from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db import get_db
from middleware.auth_middleware import get_current_user_id, get_current_admin_user
from services.order_service import OrderService


router = APIRouter(prefix="/api/orders", tags=["orders"])
order_service = OrderService()


@router.post("")
def create_order(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    result, status_code = order_service.create_order(
        db=db,
        user_id=current_user_id
    )

    return JSONResponse(
        status_code=status_code,
        content=result
    )


@router.get("")
def get_my_orders(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    result, status_code = order_service.get_my_orders(
        db=db,
        user_id=current_user_id
    )

    return JSONResponse(
        status_code=status_code,
        content=result
    )


@router.get("/admin")
def get_all_orders_admin(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    result, status_code = order_service.get_all_orders_admin(
        db=db,
        skip=skip,
        limit=limit
    )

    return JSONResponse(
        status_code=status_code,
        content=result
    )


@router.get("/admin/count")
def get_orders_count_admin(
    current_admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    result, status_code = order_service.get_orders_count_admin(db=db)

    return JSONResponse(
        status_code=status_code,
        content=result
    )


@router.get("/admin/last-month/sum")
def get_last_month_orders_sum_admin(
    current_admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    result, status_code = order_service.get_last_month_orders_sum_admin(db=db)

    return JSONResponse(
        status_code=status_code,
        content=result
    )


@router.get("/admin/last-month")
def get_last_month_orders_admin(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    result, status_code = order_service.get_last_month_orders_admin(
        db=db,
        skip=skip,
        limit=limit
    )

    return JSONResponse(
        status_code=status_code,
        content=result
    )


@router.get("/admin/{order_id}/items")
def get_order_items_by_order_id_admin(
    order_id: int,
    current_admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    result, status_code = order_service.get_order_items_by_order_id_admin(
        db=db,
        order_id=order_id
    )

    return JSONResponse(
        status_code=status_code,
        content=result
    )