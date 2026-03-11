"""
Player Repository - 球员数据访问层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.player import Player
from app.repository.base import BaseRepository


class PlayerRepository(BaseRepository[Player]):
    """球员 Repository"""

    def __init__(self, db: Session):
        super().__init__(Player, db)

    def get_by_team(self, team_id: int, skip: int = 0, limit: int = 100) -> List[Player]:
        """获取指定球队的所有球员"""
        return self.db.query(Player).filter(
            Player.team_id == team_id
        ).offset(skip).limit(limit).all()

    def get_by_position(self, position: str, skip: int = 0, limit: int = 100) -> List[Player]:
        """根据位置获取球员"""
        return self.db.query(Player).filter(
            Player.position == position
        ).offset(skip).limit(limit).all()

    def search_by_name(self, keyword: str, skip: int = 0, limit: int = 100) -> List[Player]:
        """根据姓名搜索球员"""
        return self.db.query(Player).filter(
            Player.name.ilike(f"%{keyword}%")
        ).offset(skip).limit(limit).all()

    def count_by_team(self, team_id: int) -> int:
        """统计指定球队的球员数量"""
        return self.db.query(Player).filter(
            Player.team_id == team_id
        ).count()

    def jersey_number_exists(self, team_id: int, jersey_number: int, exclude_id: Optional[int] = None) -> bool:
        """检查球衣号码在球队中是否已存在"""
        query = self.db.query(Player).filter(
            Player.team_id == team_id,
            Player.jersey_number == jersey_number
        )
        if exclude_id:
            query = query.filter(Player.id != exclude_id)
        return query.first() is not None
