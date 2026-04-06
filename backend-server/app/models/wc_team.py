from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base
from app.models.base import TimestampMixin


class WCTeam(Base, TimestampMixin):
    """世界杯球队表"""
    __tablename__ = "wc_teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    flag_url = Column(String(500), nullable=True)
    group_name = Column(String(1), nullable=False, index=True)  # A-L
    fifa_ranking = Column(Integer, nullable=True)
    confederation = Column(String(20), nullable=True)  # UEFA, CONMEBOL, etc.

    # 近期战绩
    recent_wins = Column(Integer, default=0)
    recent_draws = Column(Integer, default=0)
    recent_losses = Column(Integer, default=0)
    recent_gf = Column(Integer, default=0)  # goals for
    recent_ga = Column(Integer, default=0)  # goals against

    # 世界杯历史
    wc_appearances = Column(Integer, default=0)
    wc_best_result = Column(String(50), nullable=True)
    wc_titles = Column(Integer, default=0)

    # 补充信息
    key_players = Column(Text, nullable=True)  # JSON array string
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<WCTeam {self.name} (Group {self.group_name})>"
