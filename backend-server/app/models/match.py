from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class MatchType(str, enum.Enum):
    """比赛类型"""
    FRIENDLY = "friendly"
    LEAGUE = "league"
    CUP = "cup"
    TRAINING = "training"


class MatchStatus(str, enum.Enum):
    """比赛状态"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Match(Base, TimestampMixin):
    """比赛表"""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)

    # 主队信息
    home_team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)

    # 客队信息（对手球队）
    away_team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)

    # 比赛基本信息
    match_type = Column(String(20), default=MatchType.FRIENDLY, nullable=False)
    match_date = Column(DateTime, nullable=False, index=True)
    venue = Column(String(200), nullable=True)  # 比赛场地

    # 比分
    home_score = Column(Integer, nullable=True)  # 主队得分
    away_score = Column(Integer, nullable=True)  # 客队得分

    # 比赛状态
    status = Column(String(20), default=MatchStatus.SCHEDULED, nullable=False, index=True)

    # 备注
    notes = Column(Text, nullable=True)

    # 关系
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    player_stats = relationship("MatchPlayer", back_populates="match", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Match {self.home_team_id} vs {self.away_team_id} on {self.match_date}>"
