"""
Stats API - 统计数据接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func, desc, Integer
from app.core.database import get_db
from app.models.user import User
from app.models.match_player import MatchPlayer
from app.models.player import Player
from app.models.team import Team
from app.api.dependencies import get_optional_user
from app.utils.response import ResponseHelper

router = APIRouter()


@router.get("/goals")
async def get_top_scorers(
    limit: int = Query(10, ge=1, le=100, description="返回前N名"),
    team_id: Optional[int] = Query(None, description="按球队筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取进球榜（不需要登录）"""
    try:
        # 构建查询
        query = db.query(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            Player.jersey_number.label("jersey_number"),
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            func.coalesce(func.sum(MatchPlayer.goals), 0).label("total_goals"),
            func.coalesce(func.sum(MatchPlayer.assists), 0).label("total_assists"),
            func.sum(func.cast(MatchPlayer.played, Integer)).label("played_matches"),
            func.count(MatchPlayer.id).label("total_matches")
        ).join(
            Team, Player.team_id == Team.id
        ).outerjoin(
            MatchPlayer, Player.id == MatchPlayer.player_id
        ).group_by(
            Player.id, Player.name, Player.jersey_number, Team.id, Team.name
        )

        # 如果指定了球队，按球队筛选
        if team_id:
            query = query.filter(Player.team_id == team_id)

        # 只显示有进球的球员
        query = query.having(func.sum(MatchPlayer.goals) > 0)

        # 按总进球数排序
        results = query.order_by(desc("total_goals")).limit(limit).all()

        # 转换为返回格式
        rankings = []
        for rank, row in enumerate(results, 1):
            # 计算出勤率
            attendance_rate = (row.played_matches / row.total_matches * 100) if row.total_matches > 0 else 0

            rankings.append({
                "rank": rank,
                "player_id": row.player_id,
                "player_name": row.player_name,
                "jersey_number": row.jersey_number,
                "team_id": row.team_id,
                "team_name": row.team_name,
                "total_goals": row.total_goals,
                "total_assists": row.total_assists,
                "played_matches": row.played_matches or 0,
                "total_matches": row.total_matches,
                "attendance_rate": round(attendance_rate, 2)
            })

        return ResponseHelper.success_list(
            list_data=rankings,
            total=len(rankings),
            msg=f"获取进球榜成功"
        )
    except Exception as e:
        return ResponseHelper.error(msg=f"获取进球榜失败: {str(e)}", code=500)


@router.get("/assists")
async def get_top_assists(
    limit: int = Query(10, ge=1, le=100, description="返回前N名"),
    team_id: Optional[int] = Query(None, description="按球队筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取助攻榜（不需要登录）"""
    try:
        # 构建查询
        query = db.query(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            Player.jersey_number.label("jersey_number"),
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            func.coalesce(func.sum(MatchPlayer.goals), 0).label("total_goals"),
            func.coalesce(func.sum(MatchPlayer.assists), 0).label("total_assists"),
            func.sum(func.cast(MatchPlayer.played, Integer)).label("played_matches"),
            func.count(MatchPlayer.id).label("total_matches")
        ).join(
            Team, Player.team_id == Team.id
        ).outerjoin(
            MatchPlayer, Player.id == MatchPlayer.player_id
        ).group_by(
            Player.id, Player.name, Player.jersey_number, Team.id, Team.name
        )

        # 如果指定了球队，按球队筛选
        if team_id:
            query = query.filter(Player.team_id == team_id)

        # 只显示有助攻的球员
        query = query.having(func.sum(MatchPlayer.assists) > 0)

        # 按总助攻数排序
        results = query.order_by(desc("total_assists")).limit(limit).all()

        # 转换为返回格式
        rankings = []
        for rank, row in enumerate(results, 1):
            # 计算出勤率
            attendance_rate = (row.played_matches / row.total_matches * 100) if row.total_matches > 0 else 0

            rankings.append({
                "rank": rank,
                "player_id": row.player_id,
                "player_name": row.player_name,
                "jersey_number": row.jersey_number,
                "team_id": row.team_id,
                "team_name": row.team_name,
                "total_goals": row.total_goals,
                "total_assists": row.total_assists,
                "played_matches": row.played_matches or 0,
                "total_matches": row.total_matches,
                "attendance_rate": round(attendance_rate, 2)
            })

        return ResponseHelper.success_list(
            list_data=rankings,
            total=len(rankings),
            msg=f"获取助攻榜成功"
        )
    except Exception as e:
        return ResponseHelper.error(msg=f"获取助攻榜失败: {str(e)}", code=500)


@router.get("/attendance")
async def get_top_attendance(
    limit: int = Query(10, ge=1, le=100, description="返回前N名"),
    team_id: Optional[int] = Query(None, description="按球队筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取出勤榜（出场次数最多，不需要登录）"""
    try:
        # 构建查询
        query = db.query(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            Player.jersey_number.label("jersey_number"),
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            func.coalesce(func.sum(MatchPlayer.goals), 0).label("total_goals"),
            func.coalesce(func.sum(MatchPlayer.assists), 0).label("total_assists"),
            func.sum(func.cast(MatchPlayer.played, Integer)).label("played_matches"),
            func.count(MatchPlayer.id).label("total_matches")
        ).join(
            Team, Player.team_id == Team.id
        ).outerjoin(
            MatchPlayer, Player.id == MatchPlayer.player_id
        ).group_by(
            Player.id, Player.name, Player.jersey_number, Team.id, Team.name
        )

        # 如果指定了球队，按球队筛选
        if team_id:
            query = query.filter(Player.team_id == team_id)

        # 只显示出场过的球员
        query = query.having(func.sum(func.cast(MatchPlayer.played, Integer)) > 0)

        # 按出场次数排序
        results = query.order_by(desc("played_matches")).limit(limit).all()

        # 转换为返回格式
        rankings = []
        for rank, row in enumerate(results, 1):
            # 计算出勤率
            attendance_rate = (row.played_matches / row.total_matches * 100) if row.total_matches > 0 else 0

            rankings.append({
                "rank": rank,
                "player_id": row.player_id,
                "player_name": row.player_name,
                "jersey_number": row.jersey_number,
                "team_id": row.team_id,
                "team_name": row.team_name,
                "total_goals": row.total_goals,
                "total_assists": row.total_assists,
                "played_matches": row.played_matches or 0,
                "total_matches": row.total_matches,
                "attendance_rate": round(attendance_rate, 2)
            })

        return ResponseHelper.success_list(
            list_data=rankings,
            total=len(rankings),
            msg=f"获取出勤榜成功"
        )
    except Exception as e:
        return ResponseHelper.error(msg=f"获取出勤榜失败: {str(e)}", code=500)
