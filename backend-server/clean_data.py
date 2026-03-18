"""
清理数据库脚本
删除所有比赛数据，只保留用户账户
"""

import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.match_player import MatchPlayer
from app.models.match import Match
from app.models.player import Player
from app.models.team import Team


def clean_all_data(confirm: bool = False):
    """
    清理所有数据（除了用户）

    Args:
        confirm: 是否已确认删除（需要显式传入 True）
    """
    if not confirm:
        print("❌ 错误：需要显式确认删除操作")
        print("\n⚠️  警告：此操作将删除所有数据！")
        print("   - 所有比赛球员统计")
        print("   - 所有比赛记录")
        print("   - 所有球员")
        print("   - 所有球队")
        print("\n✅ 用户账户将被保留")
        print("\n如需执行，请运行：")
        print("  python clean_data.py --confirm")
        return

    print("\n" + "=" * 60)
    print("🗑️  开始清理数据...")
    print("=" * 60)

    db = SessionLocal()

    try:
        # 统计现有数据
        print("\n📊 当前数据统计:")
        match_players_count = db.query(MatchPlayer).count()
        matches_count = db.query(Match).count()
        players_count = db.query(Player).count()
        teams_count = db.query(Team).count()

        print(f"   比赛球员统计: {match_players_count} 条")
        print(f"   比赛记录: {matches_count} 场")
        print(f"   球员: {players_count} 位")
        print(f"   球队: {teams_count} 个")

        # 1. 删除比赛球员统计
        print("\n1️⃣  删除比赛球员统计...")
        deleted_match_players = db.query(MatchPlayer).delete()
        db.commit()
        print(f"   ✅ 已删除 {deleted_match_players} 条比赛球员统计")

        # 2. 删除比赛记录
        print("\n2️⃣  删除比赛记录...")
        deleted_matches = db.query(Match).delete()
        db.commit()
        print(f"   ✅ 已删除 {deleted_matches} 场比赛")

        # 3. 删除球员
        print("\n3️⃣  删除球员...")
        deleted_players = db.query(Player).delete()
        db.commit()
        print(f"   ✅ 已删除 {deleted_players} 位球员")

        # 4. 删除球队
        print("\n4️⃣  删除球队...")
        deleted_teams = db.query(Team).delete()
        db.commit()
        print(f"   ✅ 已删除 {deleted_teams} 个球队")

        # 验证清理结果
        print("\n📊 清理后数据统计:")
        remaining_match_players = db.query(MatchPlayer).count()
        remaining_matches = db.query(Match).count()
        remaining_players = db.query(Player).count()
        remaining_teams = db.query(Team).count()

        print(f"   比赛球员统计: {remaining_match_players} 条")
        print(f"   比赛记录: {remaining_matches} 场")
        print(f"   球员: {remaining_players} 位")
        print(f"   球队: {remaining_teams} 个")

        print("\n" + "=" * 60)
        print("✅ 数据清理完成！")
        print("=" * 60)
        print("\n💡 提示：")
        print("   - 用户账户已保留")
        print("   - 可以重新运行 import_football_data.py 导入数据")
        print("   - 或通过管理后台手动添加数据")

    except Exception as e:
        print(f"\n❌ 清理失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="清理数据库（删除所有数据，只保留用户）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
⚠️  警告：此操作不可逆！
删除的内容：
  - 所有比赛球员统计
  - 所有比赛记录
  - 所有球员
  - 所有球队

保留的内容：
  - 用户账户（admin 和其他注册用户）

示例:
  # 查看帮助（不执行删除）
  python clean_data.py

  # 确认并执行删除
  python clean_data.py --confirm
        """
    )

    parser.add_argument(
        "--confirm",
        action="store_true",
        help="确认删除数据（必须显式指定才能执行）"
    )

    args = parser.parse_args()

    clean_all_data(confirm=args.confirm)
