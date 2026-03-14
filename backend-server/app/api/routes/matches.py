"""
Matches API - 比赛接口层
只负责 HTTP 请求/响应处理，业务逻辑在 Service 层
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.schemas.match import MatchCreate, MatchUpdate, MatchResponse, MatchListResponse
from app.api.dependencies import get_current_user, get_optional_user
from app.service.match_service import MatchService
from app.service.exceptions import BusinessException
from app.utils.response import ResponseHelper

router = APIRouter()


def _match_to_dict(match) -> dict:
    """将Match对象转换为包含球队名称的字典"""
    return {
        "id": match.id,
        "home_team_id": match.home_team_id,
        "away_team_id": match.away_team_id,
        "home_team_name": match.home_team.name,
        "away_team_name": match.away_team.name,
        "match_type": match.match_type,
        "match_date": match.match_date,
        "venue": match.venue,
        "home_score": match.home_score,
        "away_score": match.away_score,
        "status": match.status,
        "notes": match.notes,
        "created_at": match.created_at,
        "updated_at": match.updated_at
    }


def _match_to_list_dict(match) -> dict:
    """将Match对象转换为列表项字典"""
    return {
        "id": match.id,
        "home_team_id": match.home_team_id,
        "away_team_id": match.away_team_id,
        "home_team_name": match.home_team.name,
        "away_team_name": match.away_team.name,
        "match_type": match.match_type,
        "match_date": match.match_date,
        "home_score": match.home_score,
        "away_score": match.away_score,
        "status": match.status,
        "venue": match.venue
    }


@router.get("/team/{team_id}")
async def get_team_matches(
    team_id: int,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取球队的所有比赛（不需要登录）"""
    try:
        service = MatchService(db)
        matches = service.get_team_matches(team_id, current_user, skip, limit)
        match_list = [_match_to_list_dict(m) for m in matches]
        return ResponseHelper.success_list(
            list_data=match_list,
            total=len(match_list),
            msg="获取比赛列表成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.get("/upcoming/{team_id}")
async def get_upcoming_matches(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取球队未来的比赛（不需要登录）"""
    try:
        service = MatchService(db)
        matches = service.get_upcoming_matches(team_id, current_user)
        match_list = [_match_to_list_dict(m) for m in matches]
        return ResponseHelper.success_list(
            list_data=match_list,
            total=len(match_list),
            msg="获取未来比赛成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.get("/recent/{team_id}")
async def get_recent_matches(
    team_id: int,
    days: int = Query(7, ge=1, le=365, description="查询最近几天的比赛（默认7天）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取球队最近几天的比赛记录（不需要登录）"""
    try:
        service = MatchService(db)
        matches = service.get_recent_matches(team_id, days, current_user)
        match_list = [_match_to_list_dict(m) for m in matches]
        return ResponseHelper.success_list(
            list_data=match_list,
            total=len(match_list),
            msg=f"获取最近{days}天比赛成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.get("/recent")
async def get_all_recent_matches(
    days: int = Query(7, ge=1, le=365, description="查询最近几天的比赛（默认7天）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取所有球队最近几天的比赛记录（不需要登录）"""
    try:
        service = MatchService(db)
        matches = service.get_all_recent_matches(days)
        match_list = [_match_to_list_dict(m) for m in matches]
        return ResponseHelper.success_list(
            list_data=match_list,
            total=len(match_list),
            msg=f"获取最近{days}天所有比赛成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.get("/{match_id}")
async def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取比赛详情（不需要登录）"""
    try:
        service = MatchService(db)
        match = service.get_match_by_id(match_id)
        match_dict = _match_to_dict(match)
        return ResponseHelper.success(data=match_dict, msg="获取比赛详情成功")
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=404)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_match(
    match_data: MatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建比赛（需要登录）"""
    try:
        service = MatchService(db)
        match = service.create_match(match_data, current_user)
        match_dict = _match_to_dict(match)
        return ResponseHelper.success(data=match_dict, msg="创建比赛成功")
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.put("/{match_id}")
async def update_match(
    match_id: int,
    match_data: MatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新比赛信息（需要登录）"""
    try:
        service = MatchService(db)
        match = service.update_match(match_id, match_data, current_user)
        match_dict = _match_to_dict(match)
        return ResponseHelper.success(data=match_dict, msg="更新比赛成功")
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.delete("/{match_id}")
async def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除比赛（需要登录）"""
    try:
        service = MatchService(db)
        service.delete_match(match_id, current_user)
        return ResponseHelper.success(msg="删除比赛成功")
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)
