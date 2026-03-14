from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime


class MatchType(str):
    """比赛类型"""
    FRIENDLY = "friendly"
    LEAGUE = "league"
    CUP = "cup"
    TRAINING = "training"


class MatchStatus(str):
    """比赛状态"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MatchBase(BaseModel):
    """比赛基础信息"""
    match_type: str = Field(default=MatchType.FRIENDLY, description="比赛类型")
    match_date: datetime = Field(..., description="比赛时间")
    venue: Optional[str] = Field(None, max_length=200, description="比赛场地")
    notes: Optional[str] = Field(None, description="备注")


class PlayerStatCreate(BaseModel):
    """球员统计数据"""
    player_id: int = Field(..., description="球员ID")
    played: bool = Field(True, description="是否出场")
    goals: int = Field(0, ge=0, description="进球数")
    assists: int = Field(0, ge=0, description="助攻数")


class MatchCreate(MatchBase):
    """创建比赛"""
    away_team_name: str = Field(..., min_length=1, max_length=100, description="客队名称（如果不存在会自动创建）")
    away_team_id: Optional[int] = Field(None, description="客队ID（可选，如果提供则不自动创建）")
    home_score: Optional[int] = Field(None, ge=0, description="主队得分")
    away_score: Optional[int] = Field(None, ge=0, description="客队得分")
    player_stats: Optional[List[PlayerStatCreate]] = Field(default=[], description="球员统计列表")


class MatchUpdate(BaseModel):
    """更新比赛"""
    match_type: Optional[str] = Field(None, description="比赛类型")
    match_date: Optional[datetime] = Field(None, description="比赛时间")
    venue: Optional[str] = Field(None, max_length=200, description="比赛场地")
    home_score: Optional[int] = Field(None, ge=0, description="主队得分")
    away_score: Optional[int] = Field(None, ge=0, description="客队得分")
    status: Optional[str] = Field(None, description="比赛状态")
    notes: Optional[str] = Field(None, description="备注")


class MatchResponse(MatchBase):
    """比赛响应"""
    id: int
    home_team_id: int
    away_team_id: int
    home_team_name: str
    away_team_name: str
    home_score: Optional[int]
    away_score: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchListResponse(BaseModel):
    """比赛列表响应"""
    id: int
    home_team_name: str
    away_team_name: str
    home_team_id: int
    away_team_id: int
    match_date: datetime
    home_score: Optional[int]
    away_score: Optional[int]
    status: str
    venue: Optional[str]

    model_config = ConfigDict(from_attributes=True)
