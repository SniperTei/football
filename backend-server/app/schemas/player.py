from pydantic import BaseModel, Field
from typing import Optional


class PlayerBase(BaseModel):
    """球员基础信息"""
    name: str = Field(..., min_length=1, max_length=100, description="球员姓名")
    position: str = Field(..., min_length=1, max_length=50, description="位置")
    jersey_number: Optional[int] = Field(None, ge=1, le=99, description="球衣号码")


class PlayerCreate(PlayerBase):
    """创建球员"""
    team_id: int = Field(..., description="所属球队ID")


class PlayerUpdate(BaseModel):
    """更新球员"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="球员姓名")
    position: Optional[str] = Field(None, min_length=1, max_length=50, description="位置")
    jersey_number: Optional[int] = Field(None, ge=1, le=99, description="球衣号码")


class PlayerResponse(PlayerBase):
    """球员响应"""
    id: int
    team_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
