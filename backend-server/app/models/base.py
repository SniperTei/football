from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from app.core.database import Base


def get_utc_datetime():
    """获取UTC时间"""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(DateTime, default=get_utc_datetime, nullable=False)
    updated_at = Column(DateTime, default=get_utc_datetime, onupdate=get_utc_datetime, nullable=False)
