from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class PermissionLevel(str):
    """权限级别"""
    READ_ONLY = "read_only"
    MEMBER = "member"
    ADMIN = "admin"
    OWNER = "owner"


class TeamMemberBase(BaseModel):
    team_id: int
    permission: str = PermissionLevel.READ_ONLY


class TeamMemberCreate(TeamMemberBase):
    user_id: int


class TeamMemberUpdate(BaseModel):
    permission: str


class TeamMemberResponse(TeamMemberBase):
    id: int
    user_id: int
    username: str
    team_name: str
    permission: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GrantPermissionRequest(BaseModel):
    """授权请求"""
    user_id: int
    team_id: int
    permission: str = PermissionLevel.MEMBER
