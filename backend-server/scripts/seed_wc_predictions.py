"""
导入本地生成的 72 场世界杯预测数据到数据库
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.wc_match import WCMatch
from app.models.wc_prediction import WCPrediction


def seed_predictions():
    db = SessionLocal()

    try:
        # 加载预测数据
        data_file = Path(__file__).parent / "wc_predictions_data.json"
        with open(data_file, "r", encoding="utf-8") as f:
            predictions_data = json.load(f)

        # 建立 match_number -> match_id 映射
        matches = db.query(WCMatch).all()
        match_map = {m.match_number: m.id for m in matches}

        created = 0
        skipped = 0

        for pred_data in predictions_data:
            match_number = pred_data["match_number"]
            match_id = match_map.get(match_number)

            if not match_id:
                print(f"  ⚠️  场次 {match_number} 不存在，跳过")
                skipped += 1
                continue

            existing = db.query(WCPrediction).filter(
                WCPrediction.match_id == match_id
            ).first()
            if existing:
                skipped += 1
                continue

            prediction = WCPrediction(
                match_id=match_id,
                home_win_prob=pred_data["home_win_prob"],
                draw_prob=pred_data["draw_prob"],
                away_win_prob=pred_data["away_win_prob"],
                predicted_home_score=pred_data["predicted_home_score"],
                predicted_away_score=pred_data["predicted_away_score"],
                reasoning=pred_data["reasoning"],
                model_version=pred_data["model_version"],
                prompt_hash=pred_data.get("prompt_hash"),
            )
            db.add(prediction)
            created += 1

        db.commit()
        print(f"✅ 预测数据导入完成: 创建 {created}, 跳过 {skipped}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_predictions()
