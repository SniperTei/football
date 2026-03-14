"""
MatchPlayer Service - 比赛球员统计业务逻辑层
"""
from typing import List
from sqlalchemy.orm import Session
from app.models.match import Match, MatchStatus
from app.models.user import User
from app.schemas.match_player import MatchPlayerUpdate
from app.repository.match_player import MatchPlayerRepository
from app.repository.match import MatchRepository
from app.repository.team import TeamRepository
from app.repository.player import PlayerRepository
from app.service.exceptions import NotFoundException, ValidationException


class MatchPlayerService:
    """比赛球员统计业务逻辑类"""

    def __init__(self, db: Session):
        self.db = db
        self.match_player_repo = MatchPlayerRepository(db)
        self.match_repo = MatchRepository(db)
        self.team_repo = TeamRepository(db)
        self.player_repo = PlayerRepository(db)

    def update_player_stats(
        self,
        match_id: int,
        player_id: int,
        stats_data: MatchPlayerUpdate,
        current_user: User
    ):
        """更新球员在比赛中的统计"""
        # 获取比赛
        match = self.match_repo.get_by_id(match_id)
        if not match:
            raise NotFoundException("比赛", match_id)

        # 获取或创建球员统计记录
        match_player = self.match_player_repo.get_player_match_stats(match_id, player_id)

        if match_player:
            # 更新现有记录
            update_dict = stats_data.model_dump(exclude_unset=True)
            match_player = self.match_player_repo.update(match_player.id, **update_dict)
        else:
            # 创建新记录
            player = self.player_repo.get_by_id(player_id)
            if not player:
                raise NotFoundException("球员", player_id)

            create_dict = stats_data.model_dump(exclude_unset=True)
            # 确保有默认值
            if 'played' not in create_dict:
                create_dict['played'] = False
            if 'goals' not in create_dict:
                create_dict['goals'] = 0
            if 'assists' not in create_dict:
                create_dict['assists'] = 0

            match_player = self.match_player_repo.create(
                match_id=match_id,
                player_id=player_id,
                team_id=player.team_id,
                **create_dict
            )

        return match_player

    def get_match_player_stats(self, match_id: int, current_user: User = None) -> List:
        """获取比赛的所有球员统计（不需要权限）"""
        match = self.match_repo.get_by_id(match_id)
        if not match:
            raise NotFoundException("比赛", match_id)

        return self.match_player_repo.get_by_match(match_id)

    def calculate_attendance_rate(self, team_id: int, player_id: int, current_user: User = None) -> dict:
        """计算球员出勤率（不需要权限）"""

        # 获取球员信息
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise NotFoundException("球员", player_id)

        # 获取球队总比赛数（已完成的）
        total_matches = self.match_repo.count_by_team_and_status(team_id, MatchStatus.COMPLETED)

        if total_matches == 0:
            return {
                'player_id': player_id,
                'player_name': player.name,
                'total_matches': 0,
                'played_matches': 0,
                'attendance_rate': 0.0,
                'total_goals': 0,
                'total_assists': 0
            }

        # 获取球员出场比赛数
        from app.models.match_player import MatchPlayer
        played_matches = self.db.query(MatchPlayer).join(
            Match, MatchPlayer.match_id == Match.id
        ).filter(
            Match.home_team_id == team_id,
            MatchPlayer.player_id == player_id,
            MatchPlayer.played == True,
            Match.status == MatchStatus.COMPLETED
        ).count()

        # 获取球员职业生涯统计
        career_stats = self.match_player_repo.get_player_career_stats(player_id)

        # 计算出勤率（百分比）
        attendance_rate = (played_matches / total_matches) * 100 if total_matches > 0 else 0.0

        return {
            'player_id': player_id,
            'player_name': player.name,
            'total_matches': total_matches,
            'played_matches': played_matches,
            'attendance_rate': round(attendance_rate, 2),
            'total_goals': career_stats['total_goals'],
            'total_assists': career_stats['total_assists']
        }

    def get_team_attendance_rates(self, team_id: int, current_user: User = None) -> List[dict]:
        """获取球队所有球员的出勤率（不需要权限）"""

        # 获取球队所有球员
        players = self.player_repo.get_all(team_id=team_id)

        attendance_rates = []
        for player in players:
            rate = self.calculate_attendance_rate(team_id, player.id, current_user)
            attendance_rates.append(rate)

        return attendance_rates
