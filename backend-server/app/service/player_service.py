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
from app.repository.match_player import MatchPlayerRepository
from app.service.exceptions import NotFoundException, DuplicateException, ValidationException


class PlayerService:
    """球员业务逻辑类"""

    def __init__(self, db: Session):
        self.db = db
        self.player_repo = PlayerRepository(db)
        self.team_repo = TeamRepository(db)
        self.match_player_repo = MatchPlayerRepository(db)

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

    def get_player_detail(self, player_id: int) -> dict:
        """获取球员详情（聚合信息：基本信息 + 生涯统计 + 出勤率 + 最近比赛）"""
        player = self.get_player_by_id(player_id)

        # 球队名称
        team = self.team_repo.get_by_id(player.team_id)
        team_name = team.name if team else '-'
        team_logo_url = team.logo_url if team else None

        # 生涯统计
        career_stats = self.match_player_repo.get_player_career_stats(player_id)

        # 出勤率
        attendance_rate = 0.0
        if career_stats['total_matches'] > 0:
            attendance_rate = round(
                (career_stats['played_matches'] / career_stats['total_matches']) * 100, 2
            )

        # 最近比赛记录（join Match 获取比赛信息）
        match_players = self.match_player_repo.get_by_player(player_id, limit=20)

        recent_matches = []
        for mp in match_players:
            match = mp.match
            if not match:
                continue

            # 判断对手
            is_home = match.home_team_id == player.team_id
            opponent_team = match.away_team if is_home else match.home_team
            opponent_name = opponent_team.name if opponent_team else '-'

            # 比分
            home_score = match.home_score if match.home_score is not None else '-'
            away_score = match.away_score if match.away_score is not None else '-'

            recent_matches.append({
                'match_id': match.id,
                'match_date': match.match_date.isoformat() if match.match_date else None,
                'match_type': match.match_type,
                'status': match.status,
                'is_home': is_home,
                'opponent_name': opponent_name,
                'home_score': home_score,
                'away_score': away_score,
                'played': mp.played,
                'goals': mp.goals,
                'assists': mp.assists,
                'yellow_cards': mp.yellow_cards,
                'red_cards': mp.red_cards,
            })

        return {
            'id': player.id,
            'name': player.name,
            'position': player.position,
            'jersey_number': player.jersey_number,
            'team_id': player.team_id,
            'team_name': team_name,
            'team_logo_url': team_logo_url,
            'created_at': player.created_at.isoformat() if player.created_at else None,
            'updated_at': player.updated_at.isoformat() if player.updated_at else None,
            'career_stats': career_stats,
            'attendance_rate': attendance_rate,
            'recent_matches': recent_matches,
        }

    def search_players(self, keyword: str) -> List[Player]:
        """搜索球员"""
        return self.player_repo.search_by_name(keyword)
