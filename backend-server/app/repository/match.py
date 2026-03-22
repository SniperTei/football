from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from app.models.match import Match, MatchStatus
from app.repository.base import BaseRepository


class MatchRepository(BaseRepository[Match]):
    """比赛 Repository"""

    def __init__(self, db: Session):
        super().__init__(Match, db)

    def get_by_team(self, team_id: int, skip: int = 0, limit: int = 100) -> List[Match]:
        """获取球队的所有比赛（主队或客队）"""
        return self.db.query(Match).filter(
            or_(
                Match.home_team_id == team_id,
                Match.away_team_id == team_id
            )
        ).order_by(Match.match_date.desc()).offset(skip).limit(limit).all()

    def get_by_team_and_status(self, team_id: int, status: str) -> List[Match]:
        """获取球队的指定状态比赛"""
        return self.db.query(Match).filter(
            and_(
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id
                ),
                Match.status == status
            )
        ).order_by(Match.match_date.desc()).all()

    def get_completed_matches(self, team_id: int) -> List[Match]:
        """获取球队已完成的比赛"""
        return self.get_by_team_and_status(team_id, MatchStatus.COMPLETED)

    def get_upcoming_matches(self, team_id: int) -> List[Match]:
        """获取球队未来的比赛"""
        return self.db.query(Match).filter(
            and_(
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id
                ),
                Match.status == MatchStatus.SCHEDULED
            )
        ).order_by(Match.match_date.asc()).all()

    def get_match_with_details(self, match_id: int) -> Optional[Match]:
        """获取比赛详情（包含球员统计）"""
        return self.db.query(Match).filter(Match.id == match_id).first()

    def count_by_team(self, team_id: int) -> int:
        """统计球队比赛总数"""
        return self.db.query(Match).filter(
            or_(
                Match.home_team_id == team_id,
                Match.away_team_id == team_id
            )
        ).count()

    def count_by_team_and_status(self, team_id: int, status: str) -> int:
        """统计球队指定状态的比赛数"""
        return self.db.query(Match).filter(
            and_(
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id
                ),
                Match.status == status
            )
        ).count()

    def get_recent_matches(self, team_id: int, days: int = 7) -> List[Match]:
        """获取最近几天的比赛记录"""
        start_date = datetime.now() - timedelta(days=days)
        return self.db.query(Match).filter(
            and_(
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id
                ),
                Match.match_date >= start_date
            )
        ).order_by(Match.match_date.desc()).all()

    def get_all_recent_matches(self, days: int = 7) -> List[Match]:
        """获取所有球队最近几天的比赛记录"""
        start_date = datetime.now() - timedelta(days=days)
        return self.db.query(Match).filter(
            Match.match_date >= start_date
        ).order_by(Match.match_date.desc()).all()

    def get_all(self, skip: int = 0, limit: int = 1000) -> List[Match]:
        """获取所有比赛记录（不分时间）"""
        return self.db.query(Match).order_by(
            Match.match_date.desc()
        ).offset(skip).limit(limit).all()
