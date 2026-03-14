from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class MatchPlayer(Base, TimestampMixin):
    """比赛球员统计表"""
    __tablename__ = "match_players"

    id = Column(Integer, primary_key=True, index=True)

    # 关联
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)

    # 出场信息
    played = Column(Boolean, default=False, nullable=False, index=True)  # 是否出场

    # 比赛数据
    goals = Column(Integer, default=0, nullable=False)  # 进球数
    assists = Column(Integer, default=0, nullable=False)  # 助攻数

    # 位置信息（比赛中实际踢的位置，可能与球员注册位置不同）
    position = Column(String(50), nullable=True)  # 比赛位置
    jersey_number = Column(Integer, nullable=True)  # 比赛球衣号码

    # 其他统计（可选，为未来扩展预留）
    minutes_played = Column(Integer, nullable=True)  # 出场时间（分钟）
    yellow_cards = Column(Integer, default=0, nullable=False)  # 黄牌
    red_cards = Column(Integer, default=0, nullable=False)  # 红牌

    # 关系
    match = relationship("Match", back_populates="player_stats")
    player = relationship("Player", back_populates="match_stats")
    team = relationship("Team")

    # 唯一约束：每个球员在每场比赛中只有一条记录
    __table_args__ = (
        UniqueConstraint('match_id', 'player_id', name='uq_match_player'),
    )

    def __repr__(self):
        return f"<MatchPlayer match_id={self.match_id} player_id={self.player_id} goals={self.goals}>"
