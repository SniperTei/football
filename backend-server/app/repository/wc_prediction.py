from typing import Optional
from sqlalchemy.orm import Session
from app.models.wc_prediction import WCPrediction
from app.repository.base import BaseRepository


class WCPredictionRepository(BaseRepository[WCPrediction]):
    def __init__(self, db: Session):
        super().__init__(WCPrediction, db)

    def get_by_match_id(self, match_id: int) -> Optional[WCPrediction]:
        return self.db.query(WCPrediction).filter(
            WCPrediction.match_id == match_id
        ).first()

    def upsert(self, match_id: int, **kwargs) -> WCPrediction:
        existing = self.get_by_match_id(match_id)
        if existing:
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            return self.create(match_id=match_id, **kwargs)

    def delete_by_match_id(self, match_id: int) -> bool:
        pred = self.get_by_match_id(match_id)
        if pred:
            self.db.delete(pred)
            self.db.commit()
            return True
        return False
