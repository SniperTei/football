"""
Team Repository - 球队数据访问层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.team import Team
from app.repository.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    """球队 Repository"""

    def __init__(self, db: Session):
        super().__init__(Team, db)

    def get_by_name(self, name: str) -> Optional[Team]:
        """根据名称获取球队"""
        return self.db.query(Team).filter(Team.name == name).first()

    def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """检查球队名是否存在（可排除指定 ID）"""
        query = self.db.query(Team).filter(Team.name == name)
        if exclude_id:
            query = query.filter(Team.id != exclude_id)
        return query.first() is not None

    def get_with_players(self, team_id: int) -> Optional[Team]:
        """获取球队及其球员"""
        return self.db.query(Team).filter(Team.id == team_id).first()

    def search(self, keyword: str) -> List[Team]:
        """搜索球队（按名称或描述）"""
        return self.db.query(Team).filter(
            (Team.name.ilike(f"%{keyword}%")) | (Team.description.ilike(f"%{keyword}%"))
        ).all()
