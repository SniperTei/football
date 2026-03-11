"""
Auth Service - 认证业务逻辑层
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, Token
from app.repository.user import UserRepository
from app.core.security import verify_password, get_password_hash, create_access_token
from app.service.exceptions import ValidationException, DuplicateException


class AuthService:
    """认证业务逻辑类"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, user_data: UserCreate) -> User:
        """用户注册"""
        # 检查用户名是否已存在
        if self.user_repo.username_exists(user_data.username):
            raise DuplicateException("用户", "用户名", user_data.username)

        # 检查邮箱是否已存在
        if self.user_repo.email_exists(user_data.email):
            raise DuplicateException("用户", "邮箱", user_data.email)

        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        return self.user_repo.create_user(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )

    def login(self, username: str, password: str):
        """用户登录，返回 token 和 user 信息"""
        # 查找用户
        user = self.user_repo.get_by_username(username)

        # 验证用户和密码
        if not user or not verify_password(password, user.hashed_password):
            raise ValidationException("用户名或密码错误")

        if not user.is_active:
            raise ValidationException("用户已被禁用")

        # 创建访问令牌
        from app.core.config import settings
        from datetime import timedelta
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return {
            "token": Token(access_token=access_token, token_type="bearer"),
            "user": user
        }
