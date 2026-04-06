from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# ==================== WCTeam ====================

class WCTeamBase(BaseModel):
    name: str
    flag_url: Optional[str] = None
    group_name: str  # A-L
    fifa_ranking: Optional[int] = None
    confederation: Optional[str] = None
    recent_wins: int = 0
    recent_draws: int = 0
    recent_losses: int = 0
    recent_gf: int = 0
    recent_ga: int = 0
    wc_appearances: int = 0
    wc_best_result: Optional[str] = None
    wc_titles: int = 0
    key_players: Optional[str] = None
    notes: Optional[str] = None


class WCTeamCreate(WCTeamBase):
    pass


class WCTeamUpdate(BaseModel):
    flag_url: Optional[str] = None
    fifa_ranking: Optional[int] = None
    confederation: Optional[str] = None
    recent_wins: Optional[int] = None
    recent_draws: Optional[int] = None
    recent_losses: Optional[int] = None
    recent_gf: Optional[int] = None
    recent_ga: Optional[int] = None
    wc_appearances: Optional[int] = None
    wc_best_result: Optional[str] = None
    wc_titles: Optional[int] = None
    key_players: Optional[str] = None
    notes: Optional[str] = None


class WCTeamResponse(WCTeamBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ==================== WCMatch ====================

class WCMatchBase(BaseModel):
    match_number: int
    stage: str = "group"
    group_name: Optional[str] = None
    match_date: Optional[datetime] = None
    venue: Optional[str] = None


class WCMatchCreate(WCMatchBase):
    home_team_id: int
    away_team_id: int


class WCMatchUpdate(BaseModel):
    match_date: Optional[datetime] = None
    venue: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: Optional[str] = None


class WCPredictionResponse(BaseModel):
    id: int
    match_id: int
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    predicted_home_score: Optional[float] = None
    predicted_away_score: Optional[float] = None
    reasoning: Optional[str] = None
    model_version: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WCMatchResponse(BaseModel):
    id: int
    match_number: int
    home_team_id: int
    away_team_id: int
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    home_team_flag: Optional[str] = None
    away_team_flag: Optional[str] = None
    stage: str
    group_name: Optional[str] = None
    match_date: Optional[datetime] = None
    venue: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str
    prediction: Optional[WCPredictionResponse] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ==================== Group Standing (computed) ====================

class GroupStandingItem(BaseModel):
    team: WCTeamResponse
    predicted_points: float
    predicted_gf: float
    predicted_ga: float
    position: int


class GroupView(BaseModel):
    group_name: str
    teams: List[GroupStandingItem]
    matches: List[WCMatchResponse]


# ==================== Prediction Generate Request ====================

class PredictionGenerateRequest(BaseModel):
    match_ids: Optional[List[int]] = None  # None = all unpredicted
    force_regenerate: bool = False
