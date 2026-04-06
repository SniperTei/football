from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.wc_match import WCMatch
from app.models.wc_prediction import WCPrediction
from app.repository.base import BaseRepository


class WCMatchRepository(BaseRepository[WCMatch]):
    def __init__(self, db: Session):
        super().__init__(WCMatch, db)

    def get_by_stage(self, stage: str) -> List[WCMatch]:
        return self.db.query(WCMatch).filter(WCMatch.stage == stage).all()

    def get_by_group(self, group_name: str) -> List[WCMatch]:
        return self.db.query(WCMatch).filter(
            WCMatch.group_name == group_name
        ).order_by(WCMatch.match_number).all()

    def get_unpredicted_matches(self) -> List[WCMatch]:
        return self.db.query(WCMatch).outerjoin(
            WCPrediction, WCMatch.id == WCPrediction.match_id
        ).filter(WCPrediction.id == None).all()  # noqa: E711

    def count_by_stage(self, stage: str) -> int:
        return self.db.query(WCMatch).filter(WCMatch.stage == stage).count()
