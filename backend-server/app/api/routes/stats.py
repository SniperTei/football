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
    year: Optional[int] = Query(None, ge=2020, le=2030, description="按年份筛选（如2024）"),
    month: Optional[int] = Query(None, ge=1, le=12, description="按月份筛选（1-12，需要与year配合使用）"),
    start_date: Optional[str] = Query(None, description="开始日期（格式：YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（格式：YYYY-MM-DD）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取进球榜（不需要登录）"""
    try:
        from datetime import datetime
        from app.models.match import Match

        # 构建基础查询 - 先获取符合条件的比赛
        match_query = db.query(Match.id)

        # 如果指定了球队，按球队筛选
        if team_id:
            match_query = match_query.filter(
                (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
            )

        # 按日期范围筛选（优先级高于year/month）
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                match_query = match_query.filter(Match.match_date >= start, Match.match_date <= end)
            except ValueError:
                return ResponseHelper.error(msg="日期格式错误，请使用 YYYY-MM-DD 格式", code=400)
        elif year:
            if month:
                # 按年月筛选
                match_query = match_query.filter(
                    func.extract('year', Match.match_date) == year,
                    func.extract('month', Match.match_date) == month
                )
            else:
                # 只按年份筛选
                match_query = match_query.filter(func.extract('year', Match.match_date) == year)

        # 获取符合条件的比赛ID列表
        match_ids = [m[0] for m in match_query.all()]
        total_matches_count = len(match_ids)

        if total_matches_count == 0:
            return ResponseHelper.success_list(list_data=[], total=0, msg="该时间段内没有比赛")

        # 构建球员统计查询
        subquery = db.query(
            MatchPlayer.player_id,
            func.sum(MatchPlayer.goals).label("total_goals"),
            func.sum(MatchPlayer.assists).label("total_assists"),
            func.sum(func.cast(MatchPlayer.played, Integer)).label("played_matches")
        ).filter(
            MatchPlayer.match_id.in_(match_ids)
        ).group_by(
            MatchPlayer.player_id
        ).subquery()

        query = db.query(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            Player.jersey_number.label("jersey_number"),
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            subquery.c.total_goals,
            subquery.c.total_assists,
            subquery.c.played_matches
        ).join(
            Team, Player.team_id == Team.id
        ).join(
            subquery, Player.id == subquery.c.player_id
        )

        # 如果指定了球队，按球队筛选
        if team_id:
            query = query.filter(Player.team_id == team_id)

        # 只显示有进球的球员
        query = query.filter(subquery.c.total_goals > 0)

        # 按总进球数排序
        results = query.order_by(desc(subquery.c.total_goals)).limit(limit).all()

        # 转换为返回格式
        rankings = []
        for rank, row in enumerate(results, 1):
            # 计算出勤率：出勤场次数 / 总比赛场数
            attendance_rate = (row.played_matches / total_matches_count * 100) if total_matches_count > 0 else 0

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
                "total_matches": total_matches_count,
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
    year: Optional[int] = Query(None, ge=2020, le=2030, description="按年份筛选（如2024）"),
    month: Optional[int] = Query(None, ge=1, le=12, description="按月份筛选（1-12，需要与year配合使用）"),
    start_date: Optional[str] = Query(None, description="开始日期（格式：YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（格式：YYYY-MM-DD）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取助攻榜（不需要登录）"""
    try:
        from datetime import datetime
        from app.models.match import Match

        # 构建基础查询 - 先获取符合条件的比赛
        match_query = db.query(Match.id)

        # 如果指定了球队，按球队筛选
        if team_id:
            match_query = match_query.filter(
                (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
            )

        # 按日期范围筛选（优先级高于year/month）
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                match_query = match_query.filter(Match.match_date >= start, Match.match_date <= end)
            except ValueError:
                return ResponseHelper.error(msg="日期格式错误，请使用 YYYY-MM-DD 格式", code=400)
        elif year:
            if month:
                # 按年月筛选
                match_query = match_query.filter(
                    func.extract('year', Match.match_date) == year,
                    func.extract('month', Match.match_date) == month
                )
            else:
                # 只按年份筛选
                match_query = match_query.filter(func.extract('year', Match.match_date) == year)

        # 获取符合条件的比赛ID列表
        match_ids = [m[0] for m in match_query.all()]
        total_matches_count = len(match_ids)

        if total_matches_count == 0:
            return ResponseHelper.success_list(list_data=[], total=0, msg="该时间段内没有比赛")

        # 构建球员统计查询
        subquery = db.query(
            MatchPlayer.player_id,
            func.sum(MatchPlayer.goals).label("total_goals"),
            func.sum(MatchPlayer.assists).label("total_assists"),
            func.sum(func.cast(MatchPlayer.played, Integer)).label("played_matches")
        ).filter(
            MatchPlayer.match_id.in_(match_ids)
        ).group_by(
            MatchPlayer.player_id
        ).subquery()

        query = db.query(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            Player.jersey_number.label("jersey_number"),
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            subquery.c.total_goals,
            subquery.c.total_assists,
            subquery.c.played_matches
        ).join(
            Team, Player.team_id == Team.id
        ).join(
            subquery, Player.id == subquery.c.player_id
        )

        # 如果指定了球队，按球队筛选
        if team_id:
            query = query.filter(Player.team_id == team_id)

        # 只显示有助攻的球员
        query = query.filter(subquery.c.total_assists > 0)

        # 按总助攻数排序
        results = query.order_by(desc(subquery.c.total_assists)).limit(limit).all()

        # 转换为返回格式
        rankings = []
        for rank, row in enumerate(results, 1):
            # 计算出勤率：出勤场次数 / 总比赛场数
            attendance_rate = (row.played_matches / total_matches_count * 100) if total_matches_count > 0 else 0

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
                "total_matches": total_matches_count,
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
    year: Optional[int] = Query(None, ge=2020, le=2030, description="按年份筛选（如2024）"),
    month: Optional[int] = Query(None, ge=1, le=12, description="按月份筛选（1-12，需要与year配合使用）"),
    start_date: Optional[str] = Query(None, description="开始日期（格式：YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（格式：YYYY-MM-DD）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取出勤榜（出场次数最多，不需要登录）"""
    try:
        from datetime import datetime
        from app.models.match import Match

        # 构建基础查询 - 先获取符合条件的比赛
        match_query = db.query(Match.id)

        # 如果指定了球队，按球队筛选
        if team_id:
            match_query = match_query.filter(
                (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
            )

        # 按日期范围筛选（优先级高于year/month）
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                match_query = match_query.filter(Match.match_date >= start, Match.match_date <= end)
            except ValueError:
                return ResponseHelper.error(msg="日期格式错误，请使用 YYYY-MM-DD 格式", code=400)
        elif year:
            if month:
                # 按年月筛选
                match_query = match_query.filter(
                    func.extract('year', Match.match_date) == year,
                    func.extract('month', Match.match_date) == month
                )
            else:
                # 只按年份筛选
                match_query = match_query.filter(func.extract('year', Match.match_date) == year)

        # 获取符合条件的比赛ID列表
        match_ids = [m[0] for m in match_query.all()]
        total_matches_count = len(match_ids)

        if total_matches_count == 0:
            return ResponseHelper.success_list(list_data=[], total=0, msg="该时间段内没有比赛")

        # 构建球员统计查询
        subquery = db.query(
            MatchPlayer.player_id,
            func.sum(MatchPlayer.goals).label("total_goals"),
            func.sum(MatchPlayer.assists).label("total_assists"),
            func.sum(func.cast(MatchPlayer.played, Integer)).label("played_matches")
        ).filter(
            MatchPlayer.match_id.in_(match_ids)
        ).group_by(
            MatchPlayer.player_id
        ).subquery()

        query = db.query(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            Player.jersey_number.label("jersey_number"),
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            subquery.c.total_goals,
            subquery.c.total_assists,
            subquery.c.played_matches
        ).join(
            Team, Player.team_id == Team.id
        ).join(
            subquery, Player.id == subquery.c.player_id
        )

        # 如果指定了球队，按球队筛选
        if team_id:
            query = query.filter(Player.team_id == team_id)

        # 只显示出场过的球员
        query = query.filter(subquery.c.played_matches > 0)

        # 按出场次数排序
        results = query.order_by(desc(subquery.c.played_matches)).limit(limit).all()

        # 转换为返回格式
        rankings = []
        for rank, row in enumerate(results, 1):
            # 计算出勤率：出勤场次数 / 总比赛场数
            attendance_rate = (row.played_matches / total_matches_count * 100) if total_matches_count > 0 else 0

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
                "total_matches": total_matches_count,
                "attendance_rate": round(attendance_rate, 2)
            })

        return ResponseHelper.success_list(
            list_data=rankings,
            total=len(rankings),
            msg=f"获取出勤榜成功"
        )
    except Exception as e:
        return ResponseHelper.error(msg=f"获取出勤榜失败: {str(e)}", code=500)


@router.get("/team/{team_id}/stats")
async def get_team_statistics(
    team_id: int,
    days: Optional[int] = Query(None, ge=1, le=3650, description="时间范围（天）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取球队统计信息（不需要登录）"""
    try:
        from app.service.match_service import MatchService
        service = MatchService(db)
        stats = service.get_team_statistics(team_id, days)
        return ResponseHelper.success(data=stats, msg="获取球队统计成功")
    except Exception as e:
        return ResponseHelper.error(msg=f"获取球队统计失败: {str(e)}", code=500)


@router.get("/team/{team_id}/head-to-head/{opponent_id}")
async def get_head_to_head_stats(
    team_id: int,
    opponent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """获取两个球队之间的对战历史（不需要登录）"""
    try:
        from app.service.match_service import MatchService
        service = MatchService(db)
        stats = service.get_head_to_head_stats(team_id, opponent_id)
        return ResponseHelper.success(data=stats, msg="获取对战历史成功")
    except Exception as e:
        return ResponseHelper.error(msg=f"获取对战历史失败: {str(e)}", code=500)
