import anthropic
import json
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class WCAIService:
    """Claude API 调用服务"""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def predict_match(self, home_team: dict, away_team: dict, stage: str = "group") -> dict:
        """
        调用 Claude API 预测比赛结果
        返回: {
            "home_win_prob": float,
            "draw_prob": float,
            "away_win_prob": float,
            "predicted_home_score": float,
            "predicted_away_score": float,
            "reasoning": str
        }
        """
        prompt = self._build_prompt(home_team, away_team, stage)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_response(response.content[0].text)
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise

    def _build_prompt(self, home: dict, away: dict, stage: str) -> str:
        return f"""You are an expert football analyst. Predict the outcome of this World Cup {stage} match.

HOME TEAM: {home['name']}
- FIFA Ranking: {home.get('fifa_ranking', 'N/A')}
- Recent Form (last 10): {home.get('recent_wins', 0)}W {home.get('recent_draws', 0)}D {home.get('recent_losses', 0)}L
- Recent Goals: {home.get('recent_gf', 0)} scored, {home.get('recent_ga', 0)} conceded
- WC Appearances: {home.get('wc_appearances', 0)}, Best: {home.get('wc_best_result', 'N/A')}, Titles: {home.get('wc_titles', 0)}
- Key Players: {home.get('key_players', 'N/A')}
- Confederation: {home.get('confederation', 'N/A')}

AWAY TEAM: {away['name']}
- FIFA Ranking: {away.get('fifa_ranking', 'N/A')}
- Recent Form (last 10): {away.get('recent_wins', 0)}W {away.get('recent_draws', 0)}D {away.get('recent_losses', 0)}L
- Recent Goals: {away.get('recent_gf', 0)} scored, {away.get('recent_ga', 0)} conceded
- WC Appearances: {away.get('wc_appearances', 0)}, Best: {away.get('wc_best_result', 'N/A')}, Titles: {away.get('wc_titles', 0)}
- Key Players: {away.get('key_players', 'N/A')}
- Confederation: {away.get('confederation', 'N/A')}

Respond ONLY with valid JSON in this exact format (no markdown, no explanation outside JSON):
{{
    "home_win_prob": <float 0-100>,
    "draw_prob": <float 0-100>,
    "away_win_prob": <float 0-100>,
    "predicted_home_score": <float>,
    "predicted_away_score": <float>,
    "reasoning": "<2-3 sentence analysis in Chinese>"
}}

The three probabilities must sum to 100. Consider rankings, form, WC experience, and confederation strength."""

    def _parse_response(self, text: str) -> dict:
        text = text.strip()
        # 去掉 markdown 代码块
        if text.startswith("```"):
            parts = text.split("```")
            text = parts[1] if len(parts) > 1 else text
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

    @staticmethod
    def compute_prompt_hash(home_team: dict, away_team: dict) -> str:
        data = json.dumps({"home": home_team, "away": away_team}, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
