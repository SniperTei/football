from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.wc_team import WCTeam
from app.repository.base import BaseRepository


class WCTeamRepository(BaseRepository[WCTeam]):
    def __init__(self, db: Session):
        super().__init__(WCTeam, db)

    def get_by_group(self, group_name: str) -> List[WCTeam]:
        return self.db.query(WCTeam).filter(
            WCTeam.group_name == group_name
        ).order_by(WCTeam.fifa_ranking).all()

    def get_all_groups(self) -> Dict[str, List[WCTeam]]:
        teams = self.db.query(WCTeam).order_by(WCTeam.group_name, WCTeam.fifa_ranking).all()
        result: Dict[str, List[WCTeam]] = {}
        for team in teams:
            result.setdefault(team.group_name, []).append(team)
        return result
