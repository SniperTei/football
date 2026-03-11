"""
TeamMember Repository - 球队成员权限数据访问层
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.team_member import TeamMember
from app.repository.base import BaseRepository


class TeamMemberRepository(BaseRepository[TeamMember]):
    """球队成员权限 Repository"""

    def __init__(self, db: Session):
        super().__init__(TeamMember, db)

    def get_user_teams(self, user_id: int) -> List[TeamMember]:
        """获取用户的所有球队权限"""
        return self.db.query(TeamMember).filter(
            TeamMember.user_id == user_id,
            TeamMember.is_active == True
        ).all()

    def get_team_members(self, team_id: int) -> List[TeamMember]:
        """获取球队的所有成员"""
        return self.db.query(TeamMember).options(
            joinedload(TeamMember.user)
        ).filter(
            TeamMember.team_id == team_id,
            TeamMember.is_active == True
        ).all()

    def get_membership(self, user_id: int, team_id: int) -> Optional[TeamMember]:
        """获取用户在指定球队的成员记录"""
        return self.db.query(TeamMember).filter(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id
        ).first()

    def user_exists_in_team(self, user_id: int, team_id: int) -> bool:
        """检查用户是否在该球队中"""
        return self.db.query(TeamMember).filter(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id
        ).first() is not None

    def add_member(self, user_id: int, team_id: int, permission: str = "read_only") -> TeamMember:
        """添加成员到球队"""
        member = TeamMember(
            user_id=user_id,
            team_id=team_id,
            permission=permission
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def update_permission(self, user_id: int, team_id: int, permission: str) -> Optional[TeamMember]:
        """更新用户在球队的权限"""
        member = self.get_membership(user_id, team_id)
        if member:
            member.permission = permission
            self.db.commit()
            self.db.refresh(member)
        return member

    def remove_member(self, user_id: int, team_id: int) -> bool:
        """移除球队成员"""
        member = self.get_membership(user_id, team_id)
        if member:
            self.db.delete(member)
            self.db.commit()
            return True
        return False
