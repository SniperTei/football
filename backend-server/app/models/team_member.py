from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class PermissionLevel(str, enum.Enum):
    """权限级别枚举"""
    READ_ONLY = "read_only"      # 只读：只能查看
    MEMBER = "member"            # 成员：可查看 + 基础操作
    ADMIN = "admin"              # 管理员：可管理该球队的所有数据
    OWNER = "owner"              # 所有者：最高权限，可删除球队


class TeamMember(Base, TimestampMixin):
    """
    球队成员权限表
    记录用户对球队的操作权限
    """
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission = Column(String(20), default=PermissionLevel.READ_ONLY, nullable=False)
    is_active = Column(Boolean, default=True)

    # 关系
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="teams")

    # 唯一约束：一个用户在一个球队只能有一条权限记录
    __table_args__ = (
        UniqueConstraint('team_id', 'user_id', name='uq_team_user'),
    )

    def __repr__(self):
        return f"<TeamMember team_id={self.team_id} user_id={self.user_id} permission={self.permission}>"
