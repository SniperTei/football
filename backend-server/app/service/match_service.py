"""
Match Service - 比赛业务逻辑层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.models.match import Match, MatchStatus
from app.models.team import Team
from app.models.user import User
from app.schemas.match import MatchCreate, MatchUpdate
from app.repository.match import MatchRepository
from app.repository.team import TeamRepository
from app.repository.match_player import MatchPlayerRepository
from app.repository.player import PlayerRepository
from app.service.exceptions import NotFoundException, ValidationException


class MatchService:
    """比赛业务逻辑类"""

    def __init__(self, db: Session):
        self.db = db
        self.match_repo = MatchRepository(db)
        self.team_repo = TeamRepository(db)
        self.match_player_repo = MatchPlayerRepository(db)
        self.player_repo = PlayerRepository(db)

    def create_match(self, match_data: MatchCreate, current_user: User) -> Match:
        """创建比赛"""
        # 自动获取用户的球队作为主队
        home_team_id = current_user.my_team_id
        if not home_team_id:
            raise ValidationException("您还没有球队，请先创建球队")

        # 验证主队是否存在
        home_team = self.team_repo.get_by_id(home_team_id)
        if not home_team:
            raise ValidationException("您的球队不存在")

        # 验证比赛日期不能是未来
        if match_data.match_date > datetime.now(timezone.utc):
            raise ValidationException("比赛日期不能是未来时间")

        # 处理客队（对手球队）
        away_team_id = match_data.away_team_id

        # 如果没有提供away_team_id，根据名称查找或创建
        if away_team_id is None:
            away_team = self.team_repo.get_by_name(match_data.away_team_name)
            if not away_team:
                # 自动创建外部球队（只填name字段）
                away_team = self.team_repo.create(name=match_data.away_team_name)
            away_team_id = away_team.id
        else:
            # 验证指定的客队是否存在
            away_team = self.team_repo.get_by_id(away_team_id)
            if not away_team:
                raise NotFoundException("客队", away_team_id)

        # 验证不能和同一支球队比赛
        if home_team_id == away_team_id:
            raise ValidationException("主队和客队不能是同一支球队")

        # 创建比赛
        match_dict = match_data.model_dump(exclude={'away_team_name', 'away_team_id', 'player_stats'})
        match_dict['home_team_id'] = home_team_id
        match_dict['away_team_id'] = away_team_id
        # 所有比赛默认为已完成状态
        match_dict['status'] = MatchStatus.COMPLETED

        match = self.match_repo.create(**match_dict)

        # 为比赛创建主队球员记录
        self._init_match_players(match.id, home_team_id, match_data.player_stats)

        return match

    def _init_match_players(self, match_id: int, team_id: int, player_stats: list = None):
        """初始化比赛球员记录"""
        # 将 player_stats 转换为字典，方便查找
        stats_dict = {}
        if player_stats:
            for stat in player_stats:
                stats_dict[stat.player_id] = stat

        # 获取球队所有球员
        players = self.player_repo.get_all(team_id=team_id)

        # 为每个球员创建比赛记录
        match_players = []
        for player in players:
            # 如果该球员有统计数据，使用它；否则默认不出场
            player_stat = stats_dict.get(player.id)
            if player_stat:
                match_players.append({
                    'match_id': match_id,
                    'player_id': player.id,
                    'team_id': team_id,
                    'played': player_stat.played,
                    'goals': player_stat.goals,
                    'assists': player_stat.assists
                })
            else:
                # 没有提供统计数据的球员，默认不出场
                match_players.append({
                    'match_id': match_id,
                    'player_id': player.id,
                    'team_id': team_id,
                    'played': False,
                    'goals': 0,
                    'assists': 0
                })

        if match_players:
            self.match_player_repo.batch_create(match_players)

    def get_match_by_id(self, match_id: int) -> Match:
        """获取比赛详情"""
        match = self.match_repo.get_match_with_details(match_id)
        if not match:
            raise NotFoundException("比赛", match_id)
        return match

    def get_team_matches(self, team_id: int, current_user: User = None, skip: int = 0, limit: int = 100) -> List[Match]:
        """获取球队的所有比赛（不需要权限）"""
        # 检查球队是否存在
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundException("球队", team_id)

        return self.match_repo.get_by_team(team_id, skip, limit)

    def update_match(self, match_id: int, match_data: MatchUpdate, current_user: User) -> Match:
        """更新比赛信息"""
        match = self.get_match_by_id(match_id)

        # 权限检查：管理员或球队拥有者才能修改
        if not current_user.is_admin and current_user.my_team_id != match.home_team_id:
            raise ValidationException("您没有权限修改这场比赛")

        # 验证更新内容
        update_dict = match_data.model_dump(exclude_unset=True)

        # 如果更新了比赛日期，验证不能是未来
        if 'match_date' in update_dict:
            if update_dict['match_date'] > datetime.now(timezone.utc):
                raise ValidationException("比赛日期不能是未来时间")

        # 如果更新比分，自动将状态改为已完成
        if 'home_score' in update_dict or 'away_score' in update_dict:
            update_dict['status'] = MatchStatus.COMPLETED

        return self.match_repo.update(match_id, **update_dict)

    def delete_match(self, match_id: int, current_user: User) -> None:
        """删除比赛"""
        match = self.get_match_by_id(match_id)

        # 权限检查：管理员或球队拥有者才能删除
        if not current_user.is_admin and current_user.my_team_id != match.home_team_id:
            raise ValidationException("您没有权限删除这场比赛")

        self.match_repo.delete(match_id)

    def get_upcoming_matches(self, team_id: int, current_user: User = None) -> List[Match]:
        """获取球队未来的比赛（不需要权限）"""
        return self.match_repo.get_upcoming_matches(team_id)

    def get_recent_matches(self, team_id: int, days: int = 7, current_user: User = None) -> List[Match]:
        """获取最近几天的比赛记录（不需要权限）"""
        # 检查球队是否存在
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundException("球队", team_id)

        # 验证天数参数（1-365天）
        if days < 1 or days > 365:
            raise ValidationException("天数必须在1-365之间")

        return self.match_repo.get_recent_matches(team_id, days)

    def get_all_recent_matches(self, days: int = 7) -> List[Match]:
        """获取所有球队最近几天的比赛记录（不需要权限）"""
        # 验证天数参数（1-365天）
        if days < 1 or days > 365:
            raise ValidationException("天数必须在1-365之间")

        return self.match_repo.get_all_recent_matches(days)

    def get_all_matches(self, skip: int = 0, limit: int = 1000) -> List[Match]:
        """获取所有比赛记录（不分时间）"""
        return self.match_repo.get_all(skip, limit)

    def get_team_statistics(self, team_id: int, days: Optional[int] = None) -> dict:
        """
        获取球队统计信息

        Args:
            team_id: 球队ID
            days: 天数筛选（None=全部, 30=最近1个月, 90=最近3个月, 365=最近1年）

        Returns:
            统计信息字典
        """
        # 检查球队是否存在
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundException("球队", team_id)

        # 获取已完成的比赛
        completed_matches = self.match_repo.get_completed_matches(team_id)

        # 按时间筛选
        if days:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            completed_matches = [m for m in completed_matches if m.match_date >= cutoff_date]

        if not completed_matches:
            return self._empty_stats()

        # 统计逻辑
        wins = draws = losses = 0
        goals_for = goals_against = 0
        home_wins = home_draws = home_losses = 0
        away_wins = away_draws = away_losses = 0
        clean_sheets = 0
        recent_form = []

        for match in completed_matches:
            is_home = match.home_team_id == team_id
            team_score = match.home_score if is_home else match.away_score
            opponent_score = match.away_score if is_home else match.home_score

            # 进球失球
            goals_for += team_score
            goals_against += opponent_score

            # 比赛结果
            if team_score > opponent_score:
                wins += 1
                if is_home:
                    home_wins += 1
                else:
                    away_wins += 1
            elif team_score == opponent_score:
                draws += 1
                if is_home:
                    home_draws += 1
                else:
                    away_draws += 1
            else:
                losses += 1
                if is_home:
                    home_losses += 1
                else:
                    away_losses += 1

            # 零封
            if opponent_score == 0:
                clean_sheets += 1

            # 最近5场
            if len(recent_form) < 5:
                recent_form.append({
                    "match_id": match.id,
                    "date": match.match_date.isoformat(),
                    "opponent": match.away_team.name if is_home else match.home_team.name,
                    "result": "W" if team_score > opponent_score else ("D" if team_score == opponent_score else "L"),
                    "score": f"{team_score}-{opponent_score}",
                    "venue": "主场" if is_home else "客场"
                })

        total = len(completed_matches)
        win_rate = (wins / total * 100) if total > 0 else 0

        return {
            "total_matches": total,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goals_for - goals_against,
            "clean_sheets": clean_sheets,
            "home_wins": home_wins,
            "home_draws": home_draws,
            "home_losses": home_losses,
            "away_wins": away_wins,
            "away_draws": away_draws,
            "away_losses": away_losses,
            "recent_form": recent_form
        }

    def get_head_to_head_stats(self, team_id: int, opponent_id: int) -> dict:
        """获取两个球队之间的对战历史"""
        matches = self.db.query(Match).filter(
            ((Match.home_team_id == team_id) & (Match.away_team_id == opponent_id)) |
            ((Match.home_team_id == opponent_id) & (Match.away_team_id == team_id))
        ).filter(Match.status == MatchStatus.COMPLETED).order_by(Match.match_date.desc()).all()

        if not matches:
            return self._empty_h2h_stats()

        team_wins = team_draws = team_losses = 0
        team_goals_for = team_goals_against = 0
        recent_matches = []

        for match in matches[:10]:
            is_home = match.home_team_id == team_id
            team_score = match.home_score if is_home else match.away_score
            opponent_score = match.away_score if is_home else match.home_score

            team_goals_for += team_score
            team_goals_against += opponent_score

            if team_score > opponent_score:
                team_wins += 1
            elif team_score == opponent_score:
                team_draws += 1
            else:
                team_losses += 1

            recent_matches.append({
                "match_id": match.id,
                "date": match.match_date.isoformat(),
                "opponent": match.away_team.name if is_home else match.home_team.name,
                "result": "W" if team_score > opponent_score else ("D" if team_score == opponent_score else "L"),
                "score": f"{team_score}-{opponent_score}",
                "venue": "主场" if is_home else "客场",
                "competition": match.match_type
            })

        return {
            "total_matches": len(matches),
            "team_wins": team_wins,
            "team_draws": team_draws,
            "team_losses": team_losses,
            "team_goals_for": team_goals_for,
            "team_goals_against": team_goals_against,
            "recent_matches": recent_matches
        }

    def _empty_stats(self) -> dict:
        """返回空统计数据"""
        return {
            "total_matches": 0,
            "wins": 0, "draws": 0, "losses": 0,
            "win_rate": 0,
            "goals_for": 0, "goals_against": 0, "goal_difference": 0,
            "clean_sheets": 0,
            "home_wins": 0, "home_draws": 0, "home_losses": 0,
            "away_wins": 0, "away_draws": 0, "away_losses": 0,
            "recent_form": []
        }

    def _empty_h2h_stats(self) -> dict:
        """返回空对战数据"""
        return {
            "total_matches": 0,
            "team_wins": 0, "team_draws": 0, "team_losses": 0,
            "team_goals_for": 0, "team_goals_against": 0,
            "recent_matches": []
        }
