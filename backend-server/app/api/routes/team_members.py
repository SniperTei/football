"""
Team Members API - 球队成员权限接口层
只负责 HTTP 请求/响应处理，业务逻辑在 Service 层
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.schemas.team_member import GrantPermissionRequest
from app.api.dependencies import get_current_user
from app.service.team_member_service import TeamMemberService
from app.service.exceptions import BusinessException
from app.utils.response import ResponseHelper

router = APIRouter()


@router.get("/teams/{team_id}/members")
async def get_team_members(
    team_id: int,
    db: Session = Depends(get_db)
):
    """获取球队的所有成员（公开）"""
    try:
        service = TeamMemberService(db)
        members = service.get_team_members(team_id)
        return ResponseHelper.success_list(
            list_data=members,
            total=len(members),
            msg="获取球队成员列表成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.get("/users/me/teams")
async def get_my_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户有权操作的所有球队"""
    try:
        service = TeamMemberService(db)
        teams = service.get_user_teams(current_user.id)
        return ResponseHelper.success_list(
            list_data=teams,
            total=len(teams),
            msg="获取我的球队列表成功"
        )
    except Exception as e:
        return ResponseHelper.error(msg=str(e), code=500)


@router.post("/permissions/grant")
async def grant_permission(
    request: GrantPermissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """授权用户操作球队（需要 ADMIN 或 OWNER 权限）"""
    try:
        service = TeamMemberService(db)
        member = service.grant_permission(current_user, request)
        return ResponseHelper.success(
            data={
                "id": member.id,
                "user_id": member.user_id,
                "team_id": member.team_id,
                "permission": member.permission,
                "is_active": member.is_active
            },
            msg="授权成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.delete("/teams/{team_id}/members/{user_id}")
async def revoke_permission(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """撤销用户对球队的操作权限（需要 OWNER 权限）"""
    try:
        service = TeamMemberService(db)
        service.revoke_permission(current_user, user_id, team_id)
        return ResponseHelper.success(msg="撤销权限成功")
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)


@router.put("/teams/{team_id}/members/{user_id}/permission")
async def update_permission(
    team_id: int,
    user_id: int,
    permission: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改用户在球队的权限级别（需要 OWNER 权限）"""
    try:
        service = TeamMemberService(db)
        member = service.update_permission(current_user, user_id, team_id, permission)
        return ResponseHelper.success(
            data={
                "id": member.id,
                "user_id": member.user_id,
                "team_id": member.team_id,
                "permission": member.permission,
                "is_active": member.is_active
            },
            msg="修改权限成功"
        )
    except BusinessException as e:
        return ResponseHelper.error(msg=str(e), code=400)
