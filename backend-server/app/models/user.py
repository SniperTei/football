from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # 超级管理员

    # 关系
    teams = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"

    def has_permission(self, team_id: int, required_permission: str) -> bool:
        """
        检查用户对指定球队的权限

        Args:
            team_id: 球队ID
            required_permission: 需要的权限级别 (read_only < member < admin < owner)

        Returns:
            bool: 是否有权限
        """
        # 超级管理员拥有所有权限
        if self.is_admin:
            return True

        # 检查用户在该球队的权限
        for team_member in self.teams:
            if team_member.team_id == team_id and team_member.is_active:
                # 权限级别判断
                permission_order = {
                    'read_only': 1,
                    'member': 2,
                    'admin': 3,
                    'owner': 4
                }
                user_level = permission_order.get(team_member.permission, 0)
                required_level = permission_order.get(required_permission, 0)
                return user_level >= required_level

        return False
