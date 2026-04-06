from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class WCPrediction(Base, TimestampMixin):
    """世界杯 AI 预测缓存表"""
    __tablename__ = "wc_predictions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("wc_matches.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # 概率（百分比 0-100）
    home_win_prob = Column(Float, nullable=False)
    draw_prob = Column(Float, nullable=False)
    away_win_prob = Column(Float, nullable=False)

    # 预测比分
    predicted_home_score = Column(Float, nullable=True)
    predicted_away_score = Column(Float, nullable=True)

    # AI 分析
    reasoning = Column(Text, nullable=True)

    # 元数据
    model_version = Column(String(50), default="claude-sonnet-4-20250514")
    prompt_hash = Column(String(64), nullable=True)  # 用于缓存失效

    # 关系
    match = relationship("WCMatch", back_populates="prediction")

    def __repr__(self):
        return f"<WCPrediction match={self.match_id} H={self.home_win_prob}% D={self.draw_prob}% A={self.away_win_prob}%>"
