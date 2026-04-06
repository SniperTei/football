from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class WCMatchStage(str, enum.Enum):
    GROUP = "group"
    ROUND_32 = "round32"
    ROUND_16 = "round16"
    QUARTER = "quarter"
    SEMI = "semi"
    THIRD_PLACE = "third_place"
    FINAL = "final"


class WCMatchStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class WCMatch(Base, TimestampMixin):
    """世界杯比赛表"""
    __tablename__ = "wc_matches"

    id = Column(Integer, primary_key=True, index=True)
    match_number = Column(Integer, unique=True, nullable=False)  # 场次编号

    # 球队
    home_team_id = Column(Integer, ForeignKey("wc_teams.id", ondelete="CASCADE"), nullable=False, index=True)
    away_team_id = Column(Integer, ForeignKey("wc_teams.id", ondelete="CASCADE"), nullable=False, index=True)

    # 阶段和分组
    stage = Column(String(20), nullable=False, index=True, default=WCMatchStage.GROUP)
    group_name = Column(String(1), nullable=True, index=True)  # 仅小组赛

    # 比赛信息
    match_date = Column(DateTime, nullable=True)
    venue = Column(String(200), nullable=True)

    # 比分
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    status = Column(String(20), default=WCMatchStatus.SCHEDULED, nullable=False)

    # 关系
    home_team = relationship("WCTeam", foreign_keys=[home_team_id])
    away_team = relationship("WCTeam", foreign_keys=[away_team_id])
    prediction = relationship("WCPrediction", back_populates="match", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WCMatch #{self.match_number} {self.home_team_id} vs {self.away_team_id}>"
