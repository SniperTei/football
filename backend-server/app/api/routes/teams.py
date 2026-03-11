"""
Teams API - 球队接口层
只负责 HTTP 请求/响应处理，业务逻辑在 Service 层
"""
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.api.dependencies import get_current_user
from app.service.team_service import TeamService
from app.service.exceptions import BusinessException
from app.utils.response import ResponseHelper

router = APIRouter()


@router.get("")
async def get_teams(db: Session = Depends(get_db)):
    """获取所有球队（公开）"""
    service = TeamService(db)
    teams = service.get_all_teams()
    return ResponseHelper.success_list(
        list_data=teams,
        total=len(teams),
        msg="获取球队列表成功"
    )


@router.get("/{team_id}")
async def get_team(team_id: int, db: Session = Depends(get_db)):
    """获取单个球队详情（公开）"""
    try:
        service = TeamService(db)
        team = service.get_team_by_id(team_id)
        return ResponseHelper.success(data=team, msg="获取球队详情成功")
    except Exception as e:
        return ResponseHelper.not_found("球队")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建球队（需要登录）"""
    try:
        service = TeamService(db)
        team = service.create_team(team_data, current_user)
        return ResponseHelper.success(data=team, msg="创建球队成功")
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.put("/{team_id}")
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新球队信息（需要登录）"""
    try:
        service = TeamService(db)
        team = service.update_team(team_id, team_data, current_user)
        return ResponseHelper.success(data=team, msg="更新球队成功")
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除球队（需要登录）"""
    try:
        service = TeamService(db)
        service.delete_team(team_id, current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)
