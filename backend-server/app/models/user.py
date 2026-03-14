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
    my_team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)  # 用户的球队

    # 关系
    my_team = relationship("Team", foreign_keys=[my_team_id])

    def __repr__(self):
        return f"<User {self.username}>"
