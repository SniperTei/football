"""
Players API - 球员接口层
只负责 HTTP 请求/响应处理，业务逻辑在 Service 层
"""
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse
from app.api.dependencies import get_current_user
from app.service.player_service import PlayerService
from app.service.exceptions import BusinessException
from app.utils.response import ResponseHelper

router = APIRouter()


@router.get("")
async def get_players(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """获取所有球员（公开）"""
    service = PlayerService(db)
    players = service.get_all_players(skip=skip, limit=limit)
    return ResponseHelper.success_list(
        list_data=players,
        total=len(players),
        msg="获取球员列表成功"
    )


@router.get("/search/{keyword}")
async def search_players(
    keyword: str,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """搜索球员（公开）"""
    service = PlayerService(db)
    players = service.search_players(keyword)
    return ResponseHelper.success_list(
        list_data=players[skip:skip+limit],
        total=len(players),
        msg="搜索球员成功"
    )


@router.get("/team/{team_id}")
async def get_players_by_team(team_id: int, db: Session = Depends(get_db)):
    """获取指定球队的所有球员（公开）"""
    try:
        service = PlayerService(db)
        players = service.get_players_by_team(team_id)
        return ResponseHelper.success_list(
            list_data=players,
            total=len(players),
            msg="获取球队球员列表成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=404)


@router.get("/{player_id}")
async def get_player(player_id: int, db: Session = Depends(get_db)):
    """获取单个球员详情（公开）"""
    try:
        service = PlayerService(db)
        player = service.get_player_by_id(player_id)
        return ResponseHelper.success(data=player, msg="获取球员详情成功")
    except Exception as e:
        return ResponseHelper.not_found("球员")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_player(
    player_data: PlayerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建球员（需要登录）"""
    try:
        service = PlayerService(db)
        player = service.create_player(player_data, current_user)
        return ResponseHelper.success(data=player, msg="创建球员成功")
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.put("/{player_id}")
async def update_player(
    player_id: int,
    player_data: PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新球员信息（需要登录）"""
    try:
        service = PlayerService(db)
        player = service.update_player(player_id, player_data, current_user)
        return ResponseHelper.success(data=player, msg="更新球员成功")
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.delete("/{player_id}")
async def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除球员（需要登录）"""
    try:
        service = PlayerService(db)
        service.delete_player(player_id, current_user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)
