from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Team(Base, TimestampMixin):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    logo_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    founded_year = Column(Integer, nullable=True)

    # 关系
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team {self.name}>"
