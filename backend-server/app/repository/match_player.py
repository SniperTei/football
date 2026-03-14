from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, Integer
from app.models.match_player import MatchPlayer
from app.repository.base import BaseRepository


class MatchPlayerRepository(BaseRepository[MatchPlayer]):
    """比赛球员统计 Repository"""

    def __init__(self, db: Session):
        super().__init__(MatchPlayer, db)

    def get_by_match(self, match_id: int) -> List[MatchPlayer]:
        """获取比赛的所有球员统计"""
        return self.db.query(MatchPlayer).filter(
            MatchPlayer.match_id == match_id
        ).all()

    def get_by_match_and_team(self, match_id: int, team_id: int) -> List[MatchPlayer]:
        """获取比赛中指定球队的球员统计"""
        return self.db.query(MatchPlayer).filter(
            and_(
                MatchPlayer.match_id == match_id,
                MatchPlayer.team_id == team_id
            )
        ).all()

    def get_by_player(self, player_id: int, skip: int = 0, limit: int = 100) -> List[MatchPlayer]:
        """获取球员的所有比赛统计"""
        return self.db.query(MatchPlayer).filter(
            MatchPlayer.player_id == player_id
        ).order_by(MatchPlayer.created_at.desc()).offset(skip).limit(limit).all()

    def get_player_match_stats(self, match_id: int, player_id: int) -> Optional[MatchPlayer]:
        """获取球员在指定比赛的统计"""
        return self.db.query(MatchPlayer).filter(
            and_(
                MatchPlayer.match_id == match_id,
                MatchPlayer.player_id == player_id
            )
        ).first()

    def count_player_matches(self, player_id: int, played: bool = None) -> int:
        """统计球员的比赛数"""
        query = self.db.query(MatchPlayer).filter(MatchPlayer.player_id == player_id)
        if played is not None:
            query = query.filter(MatchPlayer.played == played)
        return query.count()

    def get_player_career_stats(self, player_id: int) -> dict:
        """获取球员职业生涯统计"""
        stats = self.db.query(
            func.count(MatchPlayer.id).label('total_matches'),
            func.sum(MatchPlayer.played.cast(Integer)).label('played_matches'),
            func.sum(MatchPlayer.goals).label('total_goals'),
            func.sum(MatchPlayer.assists).label('total_assists'),
            func.sum(MatchPlayer.yellow_cards).label('total_yellow_cards'),
            func.sum(MatchPlayer.red_cards).label('total_red_cards')
        ).filter(MatchPlayer.player_id == player_id).first()

        return {
            'total_matches': stats.total_matches or 0,
            'played_matches': stats.played_matches or 0,
            'total_goals': stats.total_goals or 0,
            'total_assists': stats.total_assists or 0,
            'total_yellow_cards': stats.total_yellow_cards or 0,
            'total_red_cards': stats.total_red_cards or 0
        }

    def batch_create(self, match_players: List[dict]) -> List[MatchPlayer]:
        """批量创建比赛球员统计"""
        objects = [MatchPlayer(**mp) for mp in match_players]
        self.db.add_all(objects)
        self.db.commit()
        for obj in objects:
            self.db.refresh(obj)
        return objects
