"""
MatchPlayers API - 比赛球员统计接口层
只负责 HTTP 请求/响应处理，业务逻辑在 Service 层
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.match_player import MatchPlayerUpdate
from app.api.dependencies import get_current_user, get_optional_user
from app.service.match_player_service import MatchPlayerService
from app.service.exceptions import BusinessException
from app.utils.response import ResponseHelper

router = APIRouter()


@router.get("/match/{match_id}")
async def get_match_player_stats(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取比赛的所有球员统计（不需要登录）"""
    try:
        service = MatchPlayerService(db)
        stats = service.get_match_player_stats(match_id, current_user)

        # 转换为包含球员名称的字典
        stats_list = []
        for stat in stats:
            stats_dict = {
                'id': stat.id,
                'match_id': stat.match_id,
                'player_id': stat.player_id,
                'team_id': stat.team_id,
                'played': stat.played,
                'goals': stat.goals,
                'assists': stat.assists,
                'position': stat.position,
                'jersey_number': stat.jersey_number,
                'minutes_played': stat.minutes_played,
                'yellow_cards': stat.yellow_cards,
                'red_cards': stat.red_cards,
                'player_name': stat.player.name if stat.player else f"球员#{stat.player_id}",
            }
            stats_list.append(stats_dict)

        return ResponseHelper.success_list(
            list_data=stats_list,
            total=len(stats_list),
            msg="获取比赛统计成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.put("/match/{match_id}/player/{player_id}")
async def update_player_match_stats(
    match_id: int,
    player_id: int,
    stats_data: MatchPlayerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新球员在比赛中的统计（需要MEMBER权限）"""
    try:
        service = MatchPlayerService(db)
        stats = service.update_player_stats(match_id, player_id, stats_data, current_user)
        return ResponseHelper.success(data=stats, msg="更新统计成功")
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.get("/attendance/{team_id}/player/{player_id}")
async def get_player_attendance_rate(
    team_id: int,
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取球员出勤率（不需要登录）"""
    try:
        service = MatchPlayerService(db)
        rate = service.calculate_attendance_rate(team_id, player_id, current_user)
        return ResponseHelper.success(data=rate, msg="获取出勤率成功")
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.get("/attendance/{team_id}")
async def get_team_attendance_rates(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取球队所有球员的出勤率（不需要登录）"""
    try:
        service = MatchPlayerService(db)
        rates = service.get_team_attendance_rates(team_id, current_user)
        return ResponseHelper.success_list(
            list_data=rates,
            total=len(rates),
            msg="获取球队出勤率成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)
