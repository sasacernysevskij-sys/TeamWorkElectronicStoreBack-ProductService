from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db import get_db
from middleware.auth_middleware import get_current_admin_user
from services.user_service import UserService


router = APIRouter(prefix="/api/users", tags=["users"])
user_service = UserService()


@router.get("")
def get_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    result, status_code = user_service.get_users(
        db=db,
        skip=skip,
        limit=limit
    )

    return JSONResponse(
        status_code=status_code,
        content=result
    )