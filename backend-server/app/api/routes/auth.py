"""
Auth API - 认证接口层
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.service.auth_service import AuthService
from app.service.exceptions import BusinessException
from app.utils.response import ResponseHelper

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        service = AuthService(db)
        user = service.register(user_data)
        return ResponseHelper.success(
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_admin": user.is_admin
            },
            msg="注册成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    try:
        service = AuthService(db)
        result = service.login(login_data.username, login_data.password)
        return ResponseHelper.success(
            data={
                "access_token": result["token"].access_token,
                "token_type": result["token"].token_type,
                "user": {
                    "id": result["user"].id,
                    "username": result["user"].username,
                    "email": result["user"].email,
                    "is_admin": result["user"].is_admin
                }
            },
            msg="登录成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=401)
