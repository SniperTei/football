"""
Stats Service - 统计业务逻辑层
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from app.models.team import Team
from app.models.player import Player
from app.models.match import Match
from app.models.match_player_stats import MatchPlayerStats
from app.repository.team import TeamRepository
from app.service.exceptions import NotFoundException
from app.schemas.stats import (
    TeamStatsResponse,
    PlayerRankingResponse,
    HeadToHeadStats
)


class StatsService:
    """统计业务逻辑类"""

    def __init__(self, db: Session):
        self.db = db
        self.team_repo = TeamRepository(db)

    def get_team_stats(self, team_id: int) -> TeamStatsResponse:
        """获取球队统计数据"""
        # 检查球队是否存在
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundException("球队", team_id)

        # 获取球队所有比赛
        team1_matches = self.db.query(Match).filter(Match.team1_id == team_id).all()
        team2_matches = self.db.query(Match).filter(Match.team2_id == team_id).all()

        all_matches = []
        for m in team1_matches:
            result = "win" if m.team1_score > m.team2_score else ("draw" if m.team1_score == m.team2_score else "loss")
            all_matches.append({
                "goals_for": m.team1_score,
                "goals_against": m.team2_score,
                "result": result
            })
        for m in team2_matches:
            result = "win" if m.team2_score > m.team1_score else ("draw" if m.team2_score == m.team1_score else "loss")
            all_matches.append({
                "goals_for": m.team2_score,
                "goals_against": m.team1_score,
                "result": result
            })

        total_matches = len(all_matches)
        wins = sum(1 for m in all_matches if m["result"] == "win")
        draws = sum(1 for m in all_matches if m["result"] == "draw")
        losses = sum(1 for m in all_matches if m["result"] == "loss")
        goals_for = sum(m["goals_for"] for m in all_matches)
        goals_against = sum(m["goals_against"] for m in all_matches)

        goal_difference = goals_for - goals_against
        average_goals = goals_for / total_matches if total_matches > 0 else 0
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0

        return TeamStatsResponse(
            team_id=team_id,
            team_name=team.name,
            total_matches=total_matches,
            wins=wins,
            draws=draws,
            losses=losses,
            goals_for=goals_for,
            goals_against=goals_against,
            goal_difference=goal_difference,
            average_goals_per_match=round(average_goals, 2),
            win_rate=round(win_rate, 2)
        )

    def get_top_scorers(
        self, limit: int = 10, team_id: Optional[int] = None
    ) -> List[PlayerRankingResponse]:
        """获取射手榜"""
        query = self.db.query(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            func.coalesce(func.sum(MatchPlayerStats.goals), 0).label("total_goals"),
            func.count(MatchPlayerStats.id).label("total_matches")
        ).outerjoin(
            MatchPlayerStats, Player.id == MatchPlayerStats.player_id
        ).outerjoin(
            Team, Player.team_id == Team.id
        ).group_by(Player.id, Team.id)

        if team_id:
            query = query.filter(Player.team_id == team_id)

        results = query.order_by(func.sum(MatchPlayerStats.goals).desc()).limit(limit).all()

        rankings = []
        for rank, row in enumerate(results, 1):
            avg_goals = row.total_goals / row.total_matches if row.total_matches > 0 else 0
            rankings.append(PlayerRankingResponse(
                rank=rank,
                player_id=row.player_id,
                player_name=row.player_name,
                team_name=row.team_name,
                total_goals=row.total_goals,
                total_assists=0,
                total_matches=row.total_matches,
                average_goals_per_match=round(avg_goals, 2),
                average_assists_per_match=0
            ))

        return rankings

    def get_top_assists(
        self, limit: int = 10, team_id: Optional[int] = None
    ) -> List[PlayerRankingResponse]:
        """获取助攻榜"""
        query = self.db.query(
            Player.id.label("player_id"),
            Player.name.label("player_name"),
            Team.id.label("team_id"),
            Team.name.label("team_name"),
            func.coalesce(func.sum(MatchPlayerStats.assists), 0).label("total_assists"),
            func.count(MatchPlayerStats.id).label("total_matches")
        ).outerjoin(
            MatchPlayerStats, Player.id == MatchPlayerStats.player_id
        ).outerjoin(
            Team, Player.team_id == Team.id
        ).group_by(Player.id, Team.id)

        if team_id:
            query = query.filter(Player.team_id == team_id)

        results = query.order_by(func.sum(MatchPlayerStats.assists).desc()).limit(limit).all()

        rankings = []
        for rank, row in enumerate(results, 1):
            avg_assists = row.total_assists / row.total_matches if row.total_matches > 0 else 0
            rankings.append(PlayerRankingResponse(
                rank=rank,
                player_id=row.player_id,
                player_name=row.player_name,
                team_name=row.team_name,
                total_goals=0,
                total_assists=row.total_assists,
                total_matches=row.total_matches,
                average_goals_per_match=0,
                average_assists_per_match=round(avg_assists, 2)
            ))

        return rankings

    def get_head_to_head(self, team1_id: int, team2_id: int) -> HeadToHeadStats:
        """获取两队历史战绩"""
        # 检查球队是否存在
        team1 = self.team_repo.get_by_id(team1_id)
        team2 = self.team_repo.get_by_id(team2_id)

        if not team1:
            raise NotFoundException("球队", team1_id)
        if not team2:
            raise NotFoundException("球队", team2_id)

        # 获取两队之间的所有比赛
        matches = self.db.query(Match).filter(
            or_(
                and_(Match.team1_id == team1_id, Match.team2_id == team2_id),
                and_(Match.team1_id == team2_id, Match.team2_id == team1_id)
            )
        ).order_by(Match.match_date.desc()).all()

        total_matches = len(matches)
        team1_wins = 0
        team2_wins = 0
        draws = 0
        team1_goals = 0
        team2_goals = 0

        recent_matches = []
        for match in matches:
            # 判断胜负
            if match.team1_id == team1_id:
                t1_score = match.team1_score
                t2_score = match.team2_score
            else:
                t1_score = match.team2_score
                t2_score = match.team1_score

            team1_goals += t1_score
            team2_goals += t2_score

            if t1_score > t2_score:
                team1_wins += 1
            elif t2_score > t1_score:
                team2_wins += 1
            else:
                draws += 1

            # 最近5场比赛详情
            if len(recent_matches) < 5:
                recent_matches.append({
                    "match_date": match.match_date.isoformat(),
                    "team1": match.team1.name,
                    "team2": match.team2.name,
                    "team1_score": match.team1_score,
                    "team2_score": match.team2_score
                })

        team1_win_rate = (team1_wins / total_matches * 100) if total_matches > 0 else 0
        team2_win_rate = (team2_wins / total_matches * 100) if total_matches > 0 else 0

        return HeadToHeadStats(
            team1_id=team1_id,
            team1_name=team1.name,
            team2_id=team2_id,
            team2_name=team2.name,
            total_matches=total_matches,
            team1_wins=team1_wins,
            team2_wins=team2_wins,
            draws=draws,
            team1_goals_for=team1_goals,
            team2_goals_for=team2_goals,
            team1_win_rate=round(team1_win_rate, 2),
            team2_win_rate=round(team2_win_rate, 2),
            recent_matches=recent_matches
        )

    def get_league_table(self) -> List[dict]:
        """获取积分榜"""
        teams = self.db.query(Team).all()

        standings = []
        for team in teams:
            stats = self.get_team_stats(team.id)
            standings.append({
                "team_id": team.id,
                "team_name": team.name,
                "matches": stats.total_matches,
                "wins": stats.wins,
                "draws": stats.draws,
                "losses": stats.losses,
                "goals_for": stats.goals_for,
                "goals_against": stats.goals_against,
                "goal_difference": stats.goal_difference,
                "points": stats.wins * 3 + stats.draws,
                "win_rate": stats.win_rate
            })

        # 按积分、净胜球、进球数排序
        standings.sort(key=lambda x: (x["points"], x["goal_difference"], x["goals_for"]), reverse=True)

        # 添加排名
        for rank, team in enumerate(standings, 1):
            team["rank"] = rank

        return standings
