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

    def register(self, username: str, email: str, password: str,
                 team_id: Optional[int] = None,
                 create_team_data: Optional[dict] = None) -> User:
        """
        用户注册

        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            team_id: 选择现有球队的ID
            create_team_data: 创建新球队的数据
        """
        # 检查用户名是否已存在
        if self.user_repo.username_exists(username):
            raise DuplicateException("用户", "用户名", username)

        # 检查邮箱是否已存在
        if self.user_repo.email_exists(email):
            raise DuplicateException("用户", "邮箱", email)

        # 处理球队逻辑
        my_team_id = None
        if team_id:
            # 选择现有球队
            my_team_id = team_id
        elif create_team_data:
            # 创建新球队
            from app.service.team_service import TeamService
            team_service = TeamService(self.db)
            team = team_service.create(
                name=create_team_data["name"],
                description=create_team_data.get("description"),
                founded_year=create_team_data.get("founded_year")
            )
            my_team_id = team.id

        # 创建用户
        hashed_password = get_password_hash(password)
        return self.user_repo.create_user(
            username=username,
            email=email,
            hashed_password=hashed_password,
            my_team_id=my_team_id
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
