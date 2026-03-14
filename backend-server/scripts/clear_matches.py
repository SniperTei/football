"""
清空所有比赛数据

说明：
- 清空 match_players 表（比赛球员统计）
- 清空 matches 表（比赛记录）
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import get_db

def clear_matches():
    """清空所有比赛数据"""
    print("开始清空比赛数据...")

    db = next(get_db())

    try:
        # 查看当前数据
        result = db.execute(text("SELECT COUNT(*) FROM match_players"))
        match_players_count = result.scalar()
        print(f"match_players 表当前有 {match_players_count} 条记录")

        result = db.execute(text("SELECT COUNT(*) FROM matches"))
        matches_count = result.scalar()
        print(f"matches 表当前有 {matches_count} 条记录")

        # 清空 match_players 表（因为有关联关系，需要先清空）
        print("\n清空 match_players 表...")
        db.execute(text("DELETE FROM match_players"))
        db.commit()
        print("✅ match_players 表已清空")

        # 清空 matches 表
        print("清空 matches 表...")
        db.execute(text("DELETE FROM matches"))
        db.commit()
        print("✅ matches 表已清空")

        # 验证清空结果
        result = db.execute(text("SELECT COUNT(*) FROM match_players"))
        match_players_count = result.scalar()
        result = db.execute(text("SELECT COUNT(*) FROM matches"))
        matches_count = result.scalar()

        print(f"\n验证结果：")
        print(f"- match_players: {match_players_count} 条记录")
        print(f"- matches: {matches_count} 条记录")

        if match_players_count == 0 and matches_count == 0:
            print("\n✅ 所有比赛数据已成功清空！")
        else:
            print("\n⚠️  清空不完全，请检查")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_matches()
