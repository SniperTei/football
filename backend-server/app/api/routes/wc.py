from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.service.wc_service import WCService
from app.schemas.wc import (
    WCTeamCreate, WCTeamUpdate, WCMatchCreate, WCMatchUpdate,
    PredictionGenerateRequest
)
from app.utils.response import ResponseHelper

router = APIRouter()


# ==================== 公开接口 ====================

@router.get("/teams")
async def get_wc_teams(
    group: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取世界杯球队列表"""
    service = WCService(db)
    teams = service.get_all_teams()
    if group:
        teams = [t for t in teams if t.group_name == group]
    return ResponseHelper.success_list(teams, total=len(teams))


@router.get("/teams/{team_id}")
async def get_wc_team(team_id: int, db: Session = Depends(get_db)):
    """获取单支球队详情"""
    service = WCService(db)
    team = service.get_team_by_id(team_id)
    if not team:
        return ResponseHelper.not_found("球队")
    return ResponseHelper.success(data=team)


@router.get("/groups")
async def get_group_standings(db: Session = Depends(get_db)):
    """获取所有小组排名（基于 AI 预测）"""
    service = WCService(db)
    standings = service.get_group_standings()
    return ResponseHelper.success(data=[s.model_dump() for s in standings])


@router.get("/groups/{group_name}")
async def get_group_detail(group_name: str, db: Session = Depends(get_db)):
    """获取单个小组详情"""
    service = WCService(db)
    standings = service.get_group_standings()
    for group in standings:
        if group.group_name == group_name.upper():
            return ResponseHelper.success(data=group.model_dump())
    return ResponseHelper.not_found("小组")


@router.get("/matches")
async def get_wc_matches(
    stage: Optional[str] = None,
    group: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取比赛列表（含预测）"""
    service = WCService(db)
    matches = service.get_all_matches(stage=stage, group=group)
    enriched = [service.enrich_match(m) for m in matches]
    return ResponseHelper.success_list(enriched, total=len(enriched))


@router.get("/matches/{match_id}")
async def get_wc_match(match_id: int, db: Session = Depends(get_db)):
    """获取单场比赛详情"""
    service = WCService(db)
    match = service.get_match_by_id(match_id)
    if not match:
        return ResponseHelper.not_found("比赛")
    return ResponseHelper.success(data=service.enrich_match(match))


@router.get("/predictions")
async def get_predictions(
    stage: Optional[str] = None,
    group: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取预测结果"""
    service = WCService(db)
    predictions = service.get_predictions(stage=stage, group=group)
    return ResponseHelper.success_list(predictions, total=len(predictions))


# ==================== 管理接口 ====================

@router.post("/teams", status_code=201)
async def create_wc_team(
    data: WCTeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """创建世界杯球队"""
    service = WCService(db)
    try:
        team = service.create_team(data)
        return ResponseHelper.success(data=team, msg="创建成功")
    except Exception as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.put("/teams/{team_id}")
async def update_wc_team(
    team_id: int,
    data: WCTeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """更新世界杯球队"""
    service = WCService(db)
    team = service.update_team(team_id, data)
    if not team:
        return ResponseHelper.not_found("球队")
    return ResponseHelper.success(data=team, msg="更新成功")


@router.delete("/teams/{team_id}")
async def delete_wc_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """删除世界杯球队"""
    service = WCService(db)
    if not service.delete_team(team_id):
        return ResponseHelper.not_found("球队")
    return ResponseHelper.success(msg="删除成功")


@router.post("/matches", status_code=201)
async def create_wc_match(
    data: WCMatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """创建世界杯比赛"""
    service = WCService(db)
    try:
        match = service.create_match(data)
        return ResponseHelper.success(data=match, msg="创建成功")
    except Exception as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.put("/matches/{match_id}")
async def update_wc_match(
    match_id: int,
    data: WCMatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """更新世界杯比赛"""
    service = WCService(db)
    match = service.update_match(match_id, data)
    if not match:
        return ResponseHelper.not_found("比赛")
    return ResponseHelper.success(data=match, msg="更新成功")


@router.post("/predictions/generate")
async def generate_predictions(
    request: PredictionGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """触发 AI 预测生成"""
    service = WCService(db)
    try:
        result = service.generate_predictions(
            match_ids=request.match_ids,
            force=request.force_regenerate
        )
        return ResponseHelper.success(data=result, msg=f"生成完成: {result['generated']} 场预测")
    except ValueError as e:
        return ResponseHelper.error(msg=str(e), code=400)
    except Exception as e:
        return ResponseHelper.error(msg=f"预测生成失败: {str(e)}", code=500)
