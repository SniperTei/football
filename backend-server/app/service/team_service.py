"""
Team Service - 球队业务逻辑层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.team import Team
from app.models.user import User
from app.schemas.team import TeamCreate, TeamUpdate
from app.repository.team import TeamRepository
from app.service.exceptions import NotFoundException, DuplicateException, ValidationException


class TeamService:
    """球队业务逻辑类"""

    def __init__(self, db: Session):
        self.db = db
        self.team_repo = TeamRepository(db)

    def get_all_teams(self) -> List[Team]:
        """获取所有球队"""
        return self.team_repo.get_all()

    def get_team_by_id(self, team_id: int) -> Team:
        """根据 ID 获取球队"""
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundException("球队", team_id)
        return team

    def create_team(self, team_data: TeamCreate, current_user: User) -> Team:
        """创建球队"""
        # 如果用户已有球队，需要先解除
        if current_user.my_team_id:
            raise ValidationException("您已经有一个球队了，每个用户只能创建一个球队")

        # 检查球队名是否已存在
        if self.team_repo.name_exists(team_data.name):
            raise DuplicateException("球队", "名称", team_data.name)

        team = self.team_repo.create(**team_data.model_dump())

        # 设置用户的球队
        current_user.my_team_id = team.id
        self.db.commit()

        return team

    def update_team(self, team_id: int, team_data: TeamUpdate, current_user: User) -> Team:
        """更新球队"""
        # 检查球队是否存在
        team = self.get_team_by_id(team_id)

        # 如果要更新球队名，检查是否重复
        if team_data.name and team_data.name != team.name:
            if self.team_repo.name_exists(team_data.name, exclude_id=team_id):
                raise DuplicateException("球队", "名称", team_data.name)

        # 只更新提供的字段
        update_data = team_data.model_dump(exclude_unset=True)
        return self.team_repo.update(team_id, **update_data)

    def delete_team(self, team_id: int, current_user: User) -> None:
        """删除球队"""
        # 检查球队是否存在
        team = self.get_team_by_id(team_id)

        # TODO: 后续添加球员和比赛功能时，需要检查关联数据
        self.team_repo.delete(team_id)

    def search_teams(self, keyword: str) -> List[Team]:
        """搜索球队"""
        return self.team_repo.search(keyword)
