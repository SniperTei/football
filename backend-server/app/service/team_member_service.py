"""
TeamMember Service - 球队成员权限业务逻辑层
"""
from typing import List
from sqlalchemy.orm import Session
from app.models.team_member import TeamMember, PermissionLevel
from app.models.user import User
from app.schemas.team_member import GrantPermissionRequest
from app.repository.team import TeamRepository
from app.repository.team_member import TeamMemberRepository
from app.repository.user import UserRepository
from app.service.exceptions import NotFoundException, ValidationException, DuplicateException


class TeamMemberService:
    """球队成员权限业务逻辑类"""

    def __init__(self, db: Session):
        self.db = db
        self.team_member_repo = TeamMemberRepository(db)
        self.team_repo = TeamRepository(db)
        self.user_repo = UserRepository(db)

    def get_team_members(self, team_id: int) -> List[dict]:
        """获取球队的所有成员"""
        # 检查球队是否存在
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundException("球队", team_id)

        members = self.team_member_repo.get_team_members(team_id)

        result = []
        for member in members:
            result.append({
                "id": member.id,
                "user_id": member.user_id,
                "username": member.user.username,
                "email": member.user.email,
                "permission": member.permission,
                "is_active": member.is_active,
                "created_at": member.created_at,
                "updated_at": member.updated_at
            })

        return result

    def get_user_teams(self, user_id: int) -> List[dict]:
        """获取用户有权操作的所有球队"""
        members = self.team_member_repo.get_user_teams(user_id)

        result = []
        for member in members:
            result.append({
                "id": member.id,
                "team_id": member.team_id,
                "team_name": member.team.name,
                "permission": member.permission,
                "is_active": member.is_active
            })

        return result

    def grant_permission(
        self,
        grantor: User,
        request: GrantPermissionRequest
    ) -> TeamMember:
        """
        授权用户操作球队

        Args:
            grantor: 执行授权的用户（需要有权限）
            request: 授权请求
        """
        # 检查球队是否存在
        team = self.team_repo.get_by_id(request.team_id)
        if not team:
            raise NotFoundException("球队", request.team_id)

        # 检查目标用户是否存在
        target_user = self.user_repo.get_by_id(request.user_id)
        if not target_user:
            raise NotFoundException("用户", request.user_id)

        # 权限检查：只有超级管理员或球队的 owner/admin 可以授权
        if not grantor.is_admin:
            member = self.team_member_repo.get_membership(grantor.id, request.team_id)
            if not member or member.permission not in [PermissionLevel.OWNER, PermissionLevel.ADMIN]:
                raise ValidationException("您没有权限授权其他用户")

        # 不能给超级管理员授权（他们本来就有所有权限）
        if target_user.is_admin:
            raise ValidationException("超级管理员不需要授权")

        # 检查用户是否已经在球队中
        existing_member = self.team_member_repo.get_membership(request.user_id, request.team_id)
        if existing_member:
            # 更新权限
            return self.team_member_repo.update_permission(
                request.user_id,
                request.team_id,
                request.permission
            )
        else:
            # 添加新成员
            return self.team_member_repo.add_member(
                request.user_id,
                request.team_id,
                request.permission
            )

    def revoke_permission(self, grantor: User, user_id: int, team_id: int) -> None:
        """撤销用户对球队的操作权限"""
        # 权限检查
        if not grantor.is_admin:
            member = self.team_member_repo.get_membership(grantor.id, team_id)
            if not member or member.permission != PermissionLevel.OWNER:
                raise ValidationException("只有球队所有者可以撤销权限")

        success = self.team_member_repo.remove_member(user_id, team_id)
        if not success:
            raise NotFoundException("用户未在该球队中")

    def update_permission(
        self,
        grantor: User,
        user_id: int,
        team_id: int,
        permission: str
    ) -> TeamMember:
        """修改用户在球队的权限级别"""
        # 权限检查
        if not grantor.is_admin:
            grantor_member = self.team_member_repo.get_membership(grantor.id, team_id)
            if not grantor_member or grantor_member.permission != PermissionLevel.OWNER:
                raise ValidationException("只有球队所有者可以修改权限")

        member = self.team_member_repo.update_permission(user_id, team_id, permission)
        if not member:
            raise NotFoundException("用户未在该球队中")

        return member
