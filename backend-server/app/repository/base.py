"""
Repository 基类
提供通用的数据库操作方法
"""
from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repository 基类"""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """根据 ID 获取单个对象"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        """获取所有对象，支持分页和过滤"""
        query = self.db.query(self.model)

        # 动态添加过滤条件
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        return query.offset(skip).limit(limit).all()

    def create(self, **kwargs) -> ModelType:
        """创建新对象"""
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """更新对象"""
        obj = self.get_by_id(id)
        if not obj:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(obj, key):
                setattr(obj, key, value)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        """删除对象"""
        obj = self.get_by_id(id)
        if not obj:
            return False

        self.db.delete(obj)
        self.db.commit()
        return True

    def exists(self, **kwargs) -> bool:
        """检查对象是否存在"""
        return self.db.query(self.model).filter_by(**kwargs).first() is not None

    def count(self, **filters) -> int:
        """统计数量"""
        query = self.db.query(self.model)
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.count()
