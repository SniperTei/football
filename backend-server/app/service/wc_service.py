import logging
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models.wc_team import WCTeam
from app.models.wc_match import WCMatch
from app.models.wc_prediction import WCPrediction
from app.repository.wc_team import WCTeamRepository
from app.repository.wc_match import WCMatchRepository
from app.repository.wc_prediction import WCPredictionRepository
from app.service.wc_ai_service import WCAIService
from app.core.config import settings
from app.schemas.wc import (
    WCTeamCreate, WCTeamUpdate, WCMatchCreate, WCMatchUpdate,
    GroupView, GroupStandingItem
)

logger = logging.getLogger(__name__)


class WCService:
    def __init__(self, db: Session):
        self.db = db
        self.team_repo = WCTeamRepository(db)
        self.match_repo = WCMatchRepository(db)
        self.prediction_repo = WCPredictionRepository(db)

    # ==================== Team CRUD ====================

    def get_all_teams(self) -> List[WCTeam]:
        return self.team_repo.get_all(limit=1000)

    def get_team_by_id(self, team_id: int) -> Optional[WCTeam]:
        return self.team_repo.get_by_id(team_id)

    def create_team(self, data: WCTeamCreate) -> WCTeam:
        return self.team_repo.create(**data.model_dump())

    def update_team(self, team_id: int, data: WCTeamUpdate) -> Optional[WCTeam]:
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return self.team_repo.get_by_id(team_id)
        return self.team_repo.update(team_id, **update_data)

    def delete_team(self, team_id: int) -> bool:
        return self.team_repo.delete(team_id)

    # ==================== Match CRUD ====================

    def get_all_matches(self, stage: str = None, group: str = None) -> List[WCMatch]:
        if group:
            return self.match_repo.get_by_group(group)
        if stage:
            return self.match_repo.get_by_stage(stage)
        return self.match_repo.get_all(limit=1000)

    def get_match_by_id(self, match_id: int) -> Optional[WCMatch]:
        return self.match_repo.get_by_id(match_id)

    def create_match(self, data: WCMatchCreate) -> WCMatch:
        return self.match_repo.create(**data.model_dump())

    def update_match(self, match_id: int, data: WCMatchUpdate) -> Optional[WCMatch]:
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return self.match_repo.get_by_id(match_id)
        return self.match_repo.update(match_id, **update_data)

    # ==================== Match with team info ====================

    def enrich_match(self, match: WCMatch) -> dict:
        """给比赛数据添加球队名称和国旗"""
        result = {
            "id": match.id,
            "match_number": match.match_number,
            "home_team_id": match.home_team_id,
            "away_team_id": match.away_team_id,
            "home_team_name": match.home_team.name if match.home_team else None,
            "away_team_name": match.away_team.name if match.away_team else None,
            "home_team_flag": match.home_team.flag_url if match.home_team else None,
            "away_team_flag": match.away_team.flag_url if match.away_team else None,
            "stage": match.stage,
            "group_name": match.group_name,
            "match_date": match.match_date,
            "venue": match.venue,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "status": match.status,
            "created_at": match.created_at,
            "updated_at": match.updated_at,
            "prediction": None,
        }
        if match.prediction:
            pred = match.prediction
            result["prediction"] = {
                "id": pred.id,
                "match_id": pred.match_id,
                "home_win_prob": pred.home_win_prob,
                "draw_prob": pred.draw_prob,
                "away_win_prob": pred.away_win_prob,
                "predicted_home_score": pred.predicted_home_score,
                "predicted_away_score": pred.predicted_away_score,
                "reasoning": pred.reasoning,
                "model_version": pred.model_version,
                "created_at": pred.created_at,
            }
        return result

    # ==================== Predictions ====================

    def get_predictions(self, stage: str = None, group: str = None) -> List[dict]:
        matches = self.get_all_matches(stage=stage, group=group)
        return [self.enrich_match(m) for m in matches]

    def generate_predictions(self, match_ids: List[int] = None,
                             force: bool = False) -> dict:
        """生成 AI 预测"""
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("未配置 ANTHROPIC_API_KEY")

        ai_service = WCAIService(settings.ANTHROPIC_API_KEY)

        # 确定要预测的比赛
        if match_ids:
            matches = [self.match_repo.get_by_id(mid) for mid in match_ids]
            matches = [m for m in matches if m is not None]
        else:
            matches = self.match_repo.get_unpredicted_matches()

        generated = 0
        skipped = 0
        errors = 0

        for match in matches:
            try:
                home_team = match.home_team
                away_team = match.away_team

                if not home_team or not away_team:
                    skipped += 1
                    continue

                home_data = self._team_to_dict(home_team)
                away_data = self._team_to_dict(away_team)
                prompt_hash = WCAIService.compute_prompt_hash(home_data, away_data)

                # 检查缓存
                if not force:
                    existing = self.prediction_repo.get_by_match_id(match.id)
                    if existing and existing.prompt_hash == prompt_hash:
                        skipped += 1
                        continue

                # 调用 AI
                prediction = ai_service.predict_match(home_data, away_data, match.stage)

                # 缓存结果
                self.prediction_repo.upsert(
                    match_id=match.id,
                    home_win_prob=prediction["home_win_prob"],
                    draw_prob=prediction["draw_prob"],
                    away_win_prob=prediction["away_win_prob"],
                    predicted_home_score=prediction.get("predicted_home_score"),
                    predicted_away_score=prediction.get("predicted_away_score"),
                    reasoning=prediction.get("reasoning"),
                    model_version="claude-sonnet-4-20250514",
                    prompt_hash=prompt_hash,
                )
                generated += 1
                logger.info(f"Predicted match #{match.match_number}: {home_team.name} vs {away_team.name}")

            except Exception as e:
                errors += 1
                logger.error(f"Failed to predict match {match.id}: {e}")

        return {"generated": generated, "skipped": skipped, "errors": errors}

    # ==================== Group Standings ====================

    def get_group_standings(self) -> List[GroupView]:
        """计算所有小组的预测排名"""
        all_groups = self.team_repo.get_all_groups()
        result = []

        for group_name in sorted(all_groups.keys()):
            teams = all_groups[group_name]
            matches = self.match_repo.get_by_group(group_name)

            # 计算每支球队的预测积分
            team_stats: Dict[int, dict] = {
                t.id: {"team": t, "predicted_points": 0.0, "predicted_gf": 0.0, "predicted_ga": 0.0}
                for t in teams
            }

            for match in matches:
                if not match.prediction:
                    continue
                pred = match.prediction
                hid, aid = match.home_team_id, match.away_team_id

                if hid in team_stats:
                    team_stats[hid]["predicted_points"] += 3 * pred.home_win_prob / 100 + 1 * pred.draw_prob / 100
                    team_stats[hid]["predicted_gf"] += pred.predicted_home_score or 0
                    team_stats[hid]["predicted_ga"] += pred.predicted_away_score or 0

                if aid in team_stats:
                    team_stats[aid]["predicted_points"] += 3 * pred.away_win_prob / 100 + 1 * pred.draw_prob / 100
                    team_stats[aid]["predicted_gf"] += pred.predicted_away_score or 0
                    team_stats[aid]["predicted_ga"] += pred.predicted_home_score or 0

            # 排序
            sorted_stats = sorted(
                team_stats.values(),
                key=lambda x: (x["predicted_points"], x["predicted_gf"] - x["predicted_ga"]),
                reverse=True
            )

            standings = [
                GroupStandingItem(
                    team=s["team"],
                    predicted_points=round(s["predicted_points"], 1),
                    predicted_gf=round(s["predicted_gf"], 1),
                    predicted_ga=round(s["predicted_ga"], 1),
                    position=i + 1,
                )
                for i, s in enumerate(sorted_stats)
            ]

            enriched_matches = [self.enrich_match(m) for m in matches]
            result.append(GroupView(
                group_name=group_name,
                teams=standings,
                matches=enriched_matches,
            ))

        return result

    # ==================== Helpers ====================

    @staticmethod
    def _team_to_dict(team: WCTeam) -> dict:
        return {
            "name": team.name,
            "fifa_ranking": team.fifa_ranking,
            "confederation": team.confederation,
            "recent_wins": team.recent_wins,
            "recent_draws": team.recent_draws,
            "recent_losses": team.recent_losses,
            "recent_gf": team.recent_gf,
            "recent_ga": team.recent_ga,
            "wc_appearances": team.wc_appearances,
            "wc_best_result": team.wc_best_result,
            "wc_titles": team.wc_titles,
            "key_players": team.key_players,
        }
