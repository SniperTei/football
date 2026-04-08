import httpx
import json
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class WCAIService:
    """AI 预测服务，支持 OpenAI 兼容 API（智谱等）"""

    def __init__(self, api_key: str, base_url: str = "", model: str = "glm-4"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") if base_url else "https://open.bigmodel.cn/api/paas/v4"
        self.model = model

    def predict_match(self, home_team: dict, away_team: dict, stage: str = "group") -> dict:
        prompt = self._build_prompt(home_team, away_team, stage)

        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 2048,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            return self._parse_response(text)
        except httpx.HTTPStatusError as e:
            logger.error(f"AI API call failed: {e.response.status_code} {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
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
    "reasoning": "<detailed analysis in Chinese, 150-300 words, covering: 1)双方实力对比与排名分析 2)近期状态与攻防表现 3)世界杯经验与心理因素 4)关键球员对决与战术看点 5)最终预测依据总结>"
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
