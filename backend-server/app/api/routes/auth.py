"""
Auth API - 认证接口层
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.service.auth_service import AuthService
from app.service.team_service import TeamService
from app.service.exceptions import BusinessException
from app.utils.response import ResponseHelper

router = APIRouter()


class RegisterSelectExisting(BaseModel):
    """选择现有球队注册"""
    register_type: str = Field(default="select_existing", pattern="^select_existing$")
    username: str
    email: EmailStr
    password: str
    team_id: int = Field(..., description="选择的球队ID")


class RegisterCreateNew(BaseModel):
    """创建新球队注册"""
    register_type: str = Field(default="create_new", pattern="^create_new$")
    username: str
    email: EmailStr
    password: str
    team_name: str = Field(..., min_length=2, max_length=50, description="球队名称")
    team_description: Optional[str] = Field(None, max_length=200, description="球队描述")
    founded_year: Optional[int] = Field(None, ge=1900, le=2030, description="成立年份")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册（简单版本，不选择球队）"""
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


@router.post("/register/enhanced", status_code=status.HTTP_201_CREATED)
async def register_enhanced(
    user_data: RegisterSelectExisting | RegisterCreateNew,
    db: Session = Depends(get_db)
):
    """
    增强的用户注册

    支持两种注册方式：
    1. 选择现有球队（register_type=select_existing）：需要提供 team_id
    2. 创建新球队（register_type=create_new）：需要提供 team_name

    使用方式：
    - 选择现有球队：{"register_type": "select_existing", "username": "test", "email": "test@example.com", "password": "123456", "team_id": 1}
    - 创建新球队：{"register_type": "create_new", "username": "test", "email": "test@example.com", "password": "123456", "team_name": "新球队", "team_description": "描述", "founded_year": 2024}
    """
    try:
        auth_service = AuthService(db)
        team_service = TeamService(db)

        # 根据注册类型分发
        if user_data.register_type == "select_existing":
            # 选择现有球队注册
            user = auth_service.register(
                username=user_data.username,
                email=user_data.email,
                password=user_data.password,
                team_id=user_data.team_id
            )

            team = team_service.get_by_id(user_data.team_id)

            return ResponseHelper.success(
                data={
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "my_team_id": user.my_team_id,
                        "is_admin": user.is_admin
                    },
                    "team": {
                        "id": team.id,
                        "name": team.name,
                        "description": team.description
                    },
                    "message": "注册成功，已加入球队：" + team.name
                },
                msg="注册成功"
            )

        elif user_data.register_type == "create_new":
            # 创建新球队注册
            user = auth_service.register(
                username=user_data.username,
                email=user_data.email,
                password=user_data.password,
                create_team_data={
                    "name": user_data.team_name,
                    "description": user_data.team_description or f"{user_data.team_name}足球俱乐部",
                    "founded_year": user_data.founded_year
                }
            )

            team = team_service.get_by_id(user.my_team_id)

            return ResponseHelper.success(
                data={
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "my_team_id": user.my_team_id,
                        "is_admin": user.is_admin
                    },
                    "team": {
                        "id": team.id,
                        "name": team.name,
                        "description": team.description,
                        "founded_year": team.founded_year
                    },
                    "is_team_owner": True,
                    "message": "注册成功，已创建球队：" + team.name + "，您已成为球队队长"
                },
                msg="注册成功"
            )

    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)
    except Exception as e:
        return ResponseHelper.error(msg=f"注册失败: {str(e)}", code=500)


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
                    "my_team_id": result["user"].my_team_id,
                    "is_admin": result["user"].is_admin
                }
            },
            msg="登录成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=401)
