"""
Player Service - 球员业务逻辑层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.player import Player
from app.models.user import User
from app.schemas.player import PlayerCreate, PlayerUpdate
from app.repository.player import PlayerRepository
from app.repository.team import TeamRepository
from app.service.exceptions import NotFoundException, DuplicateException, ValidationException


class PlayerService:
    """球员业务逻辑类"""

    def __init__(self, db: Session):
        self.db = db
        self.player_repo = PlayerRepository(db)
        self.team_repo = TeamRepository(db)

    def get_all_players(self, skip: int = 0, limit: int = 100) -> List[Player]:
        """获取所有球员"""
        return self.player_repo.get_all(skip=skip, limit=limit)

    def get_player_by_id(self, player_id: int) -> Player:
        """根据 ID 获取球员"""
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise NotFoundException("球员", player_id)
        return player

    def get_players_by_team(self, team_id: int) -> List[Player]:
        """获取指定球队的所有球员"""
        # 检查球队是否存在
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundException("球队", team_id)

        return self.player_repo.get_by_team(team_id)

    def create_player(self, player_data: PlayerCreate, current_user: User) -> Player:
        """创建球员"""
        # 检查球队是否存在
        team = self.team_repo.get_by_id(player_data.team_id)
        if not team:
            raise NotFoundException("球队", player_data.team_id)

        # 检查球衣号码是否已被使用
        if player_data.jersey_number:
            if self.player_repo.jersey_number_exists(
                player_data.team_id,
                player_data.jersey_number
            ):
                raise DuplicateException("球员", "球衣号码", str(player_data.jersey_number))

        player = self.player_repo.create(**player_data.model_dump())
        return player

    def update_player(self, player_id: int, player_data: PlayerUpdate, current_user: User) -> Player:
        """更新球员信息"""
        # 检查球员是否存在
        player = self.get_player_by_id(player_id)

        # 如果要更新球衣号码，检查是否重复
        if player_data.jersey_number and player_data.jersey_number != player.jersey_number:
            if self.player_repo.jersey_number_exists(
                player.team_id,
                player_data.jersey_number,
                exclude_id=player_id
            ):
                raise DuplicateException("球员", "球衣号码", str(player_data.jersey_number))

        # 只更新提供的字段
        update_data = player_data.model_dump(exclude_unset=True)
        return self.player_repo.update(player_id, **update_data)

    def delete_player(self, player_id: int, current_user: User) -> None:
        """删除球员"""
        # 检查球员是否存在
        player = self.get_player_by_id(player_id)
        self.player_repo.delete(player_id)

    def search_players(self, keyword: str) -> List[Player]:
        """搜索球员"""
        return self.player_repo.search_by_name(keyword)
