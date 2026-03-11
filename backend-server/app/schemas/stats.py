from pydantic import BaseModel
from typing import Optional


class TeamStatsResponse(BaseModel):
    """球队统计响应"""
    team_id: int
    team_name: str
    total_matches: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    average_goals_per_match: float
    win_rate: float


class PlayerRankingResponse(BaseModel):
    """球员排名响应（射手榜/助攻榜）"""
    rank: int
    player_id: int
    player_name: str
    team_name: str
    total_goals: Optional[int] = 0
    total_assists: Optional[int] = 0
    total_matches: int
    average_goals_per_match: Optional[float] = 0
    average_assists_per_match: Optional[float] = 0


class HeadToHeadStats(BaseModel):
    """两队历史战绩统计"""
    team1_id: int
    team1_name: str
    team2_id: int
    team2_name: str
    total_matches: int
    team1_wins: int
    team2_wins: int
    draws: int
    team1_goals_for: int
    team2_goals_for: int
    team1_win_rate: float
    team2_win_rate: float
    recent_matches: list
