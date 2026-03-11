"""
User Repository - 用户数据访问层
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """用户 Repository"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()

    def username_exists(self, username: str) -> bool:
        """检查用户名是否存在"""
        return self.db.query(User).filter(User.username == username).first() is not None

    def email_exists(self, email: str) -> bool:
        """检查邮箱是否存在"""
        return self.db.query(User).filter(User.email == email).first() is not None

    def create_user(self, username: str, email: str, hashed_password: str, **kwargs) -> User:
        """创建用户"""
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            **kwargs
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
