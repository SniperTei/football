from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class MatchPlayerBase(BaseModel):
    """比赛球员基础信息"""
    played: bool = Field(default=False, description="是否出场")
    goals: int = Field(default=0, ge=0, description="进球数")
    assists: int = Field(default=0, ge=0, description="助攻数")
    position: Optional[str] = Field(None, max_length=50, description="比赛位置")
    jersey_number: Optional[int] = Field(None, ge=1, le=99, description="比赛球衣号码")
    minutes_played: Optional[int] = Field(None, ge=0, description="出场时间（分钟）")
    yellow_cards: int = Field(default=0, ge=0, description="黄牌数")
    red_cards: int = Field(default=0, ge=0, description="红牌数")


class MatchPlayerCreate(MatchPlayerBase):
    """创建比赛球员统计"""
    player_id: int = Field(..., description="球员ID")


class MatchPlayerUpdate(BaseModel):
    """更新比赛球员统计"""
    played: Optional[bool] = Field(None, description="是否出场")
    goals: Optional[int] = Field(None, ge=0, description="进球数")
    assists: Optional[int] = Field(None, ge=0, description="助攻数")
    position: Optional[str] = Field(None, max_length=50, description="比赛位置")
    jersey_number: Optional[int] = Field(None, ge=1, le=99, description="比赛球衣号码")
    minutes_played: Optional[int] = Field(None, ge=0, description="出场时间（分钟）")
    yellow_cards: Optional[int] = Field(None, ge=0, description="黄牌数")
    red_cards: Optional[int] = Field(None, ge=0, description="红牌数")


class MatchPlayerResponse(MatchPlayerBase):
    """比赛球员统计响应"""
    id: int
    match_id: int
    player_id: int
    player_name: str
    team_id: int
    team_name: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class AttendanceRateResponse(BaseModel):
    """出勤率响应"""
    player_id: int
    player_name: str
    total_matches: int  # 球队总比赛数
    played_matches: int  # 球员出场比赛数
    attendance_rate: float  # 出勤率（百分比）
    total_goals: int  # 总进球数
    total_assists: int  # 总助攻数


class TeamMatchStatsResponse(BaseModel):
    """球队比赛统计响应"""
    team_id: int
    team_name: str
    total_matches: int
    wins: int
    draws: int
    losses: int
    goals_for: int  # 进球数
    goals_against: int  # 失球数
