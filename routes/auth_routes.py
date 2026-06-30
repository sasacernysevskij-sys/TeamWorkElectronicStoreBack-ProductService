from fastapi import APIRouter, Depends, HTTPException
from middleware.auth_middleware import get_current_user_id
from models.user import User
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from db import get_db
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    surname: str
    phone: str = ""
class LoginRequest(BaseModel):
    email: str
    password: str
class ForgotPasswordRequest(BaseModel):
    email: str
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    result, status_code = auth_service.register(
        db=db,
        email=data.email,
        password=data.password,
        name=data.name,
        surname=data.surname,
        phone=data.phone
    )
    return result


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result, status_code = auth_service.login(
        db=db,
        email=data.email,
        password=data.password
    )
    return result

#Тестовый запрос для проверки авторизации
@router.get("/me")
def get_me(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    return {
        "message": "Ты авторизован",
        "user": {
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "created_at": user.created_at
        }
    }
@router.post("/make-admin")
def make_admin(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"error": "Пользователь не найден"}
    user.role = "admin"
    db.commit()
    return {"message": f"Пользователь {email} теперь админ"}
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    result, status_code = auth_service.forgot_password(db=db, email=data.email)
    return JSONResponse(status_code=status_code, content=result)
@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    result, status_code = auth_service.reset_password(
        db=db, token=data.token, new_password=data.new_password
    )
    return JSONResponse(status_code=status_code, content=result)