from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Player(Base, TimestampMixin):
    """
    球员表
    """
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    position = Column(String(50), nullable=False)  # 位置：前锋、中场、后卫、门将
    jersey_number = Column(Integer, nullable=True)  # 球衣号码

    # 关系
    team = relationship("Team", back_populates="players")
    match_stats = relationship("MatchPlayer", back_populates="player", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Player {self.name} ({self.position})>"
