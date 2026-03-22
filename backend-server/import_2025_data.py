"""
梅州客家队 2025 年数据导入脚本
从 my_football_data.xlsx 导入 2025 年比赛数据到数据库
"""

import sys
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.team import Team
from app.models.player import Player
from app.models.match import Match, MatchType, MatchStatus
from app.models.match_player import MatchPlayer


def excel_date_to_serial(excel_date):
    """将 Excel 日期序列号转换为 Python 日期"""
    if pd.isna(excel_date):
        return None

    try:
        # Excel 的基准日期是 1899-12-30
        excel_epoch = datetime(1899, 12, 30)
        converted_date = excel_epoch + timedelta(days=int(excel_date))

        # 只导入 2025 年的数据
        if converted_date.year != 2025:
            return None

        return converted_date
    except (ValueError, TypeError):
        return None


def parse_score(score_str):
    """解析比分字符串 '5:3' -> (5, 3)"""
    if pd.isna(score_str) or not isinstance(score_str, str):
        return None, None

    try:
        parts = score_str.split(':')
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    except (ValueError, AttributeError):
        pass

    return None, None


def import_2025_football_data(excel_file: str, home_team_name: str = "梅州客家队", dry_run: bool = False):
    """
    导入 2025 年足球数据

    Args:
        excel_file: Excel 文件路径
        home_team_name: 主队名称（默认"梅州客家队"）
        dry_run: 干运行模式，只读取数据不实际导入
    """
    mode = "🔍 干运行模式" if dry_run else "💾 导入模式"
    print(f"\n{mode}: {excel_file}")
    print("=" * 70)

    if dry_run:
        print("\n⚠️  干运行模式：只读取并显示数据，不会修改数据库\n")

    # 创建数据库会话
    db = SessionLocal() if not dry_run else None

    try:
        # 读取 Excel 文件的第一个 sheet
        print("\n1️⃣  读取 Excel 文件（Sheet: 2025进球、助攻）...")
        df = pd.read_excel(excel_file, sheet_name='2025进球、助攻')
        print(f"   ✅ 读取到 {len(df)} 行数据")

        # 跳过第一行（标题行），从第二行开始是实际数据
        data_df = df.iloc[1:].reset_index(drop=True)

        # 提取球员名单（每隔一列，跳过"进球"和"助攻"列）
        print("\n2️⃣  提取球员名单...")
        player_names = []
        for i in range(3, len(df.columns), 2):
            col_name = df.columns[i]
            if pd.notna(col_name) and col_name != 'Unnamed' and col_name != '对手':
                player_names.append(col_name)

        print(f"   ✅ 发现 {len(player_names)} 位球员:")
        for idx, name in enumerate(player_names, 1):
            print(f"      {idx:2d}. {name}")

        if dry_run:
            # 干运行模式：只显示将要导入的数据摘要
            print(f"\n3️⃣  数据预览（前 5 场 2025 年比赛）:")
            print("-" * 70)

            matches_preview = []
            matches_2024_count = 0

            for idx, row in data_df.iterrows():
                date_value = row['日期']
                opponent_name = row['对手']
                score_str = row['比分']

                if pd.isna(date_value) or pd.isna(opponent_name):
                    continue

                match_date = excel_date_to_serial(date_value)
                if not match_date:
                    # 不是 2025 年的数据
                    matches_2024_count += 1
                    continue

                if len(matches_preview) >= 5:
                    break

                # 统计该场比赛的球员数据
                players_with_stats = []
                for player_name in player_names:
                    goals_col = player_name
                    assists_col = df.columns[df.columns.get_loc(player_name) + 1]

                    goals_value = row[goals_col]
                    assists_value = row[assists_col]

                    if pd.notna(goals_value) or pd.notna(assists_value):
                        goals = int(goals_value) if pd.notna(goals_value) and str(goals_value).strip() != '' else 0
                        assists = int(assists_value) if pd.notna(assists_value) and str(assists_value).strip() != '' else 0

                        if goals > 0 or assists > 0:
                            players_with_stats.append(f"{player_name}({goals}球{assists}助)")

                matches_preview.append({
                    'date': match_date.strftime('%Y-%m-%d'),
                    'opponent': opponent_name,
                    'score': score_str,
                    'players': players_with_stats
                })

            if matches_2024_count > 0:
                print(f"   ℹ️  已过滤 {matches_2024_count} 场非 2025 年的比赛")

            for match in matches_preview:
                print(f"\n   📅 {match['date']} vs {match['opponent']} ({match['score']})")
                if match['players']:
                    for player in match['players'][:5]:  # 只显示前 5 个
                        print(f"      • {player}")
                    if len(match['players']) > 5:
                        print(f"      ... 等 {len(match['players'])} 位球员有数据")

            print("\n" + "=" * 70)
            print("✅ 干运行完成！以上是数据预览。")
            print(f"   如需实际导入，请运行: python import_2025_data.py")
            print("=" * 70)
            return

        # 正式导入模式
        # 创建或获取主队
        print(f"\n3️⃣  创建主队: {home_team_name}")
        home_team = get_or_create_team(db, home_team_name, founded_year=2025)

        # 创建或获取球员
        print("\n4️⃣  创建球员...")
        players = {}
        for idx, player_name in enumerate(player_names, 1):
            player = get_or_create_player(db, home_team, player_name, jersey_number=idx)
            players[player_name] = player

        # 导入比赛数据
        print("\n5️⃣  导入 2025 年比赛数据...")
        matches_created = 0
        matches_skipped = 0
        matches_2024_filtered = 0
        match_stats_created = 0

        for idx, row in data_df.iterrows():
            # 获取比赛基本信息
            date_value = row['日期']
            opponent_name = row['对手']
            score_str = row['比分']

            # 跳过无效数据
            if pd.isna(date_value) or pd.isna(opponent_name):
                continue

            # 转换日期（只保留 2025 年的数据）
            match_date = excel_date_to_serial(date_value)
            if not match_date:
                matches_2024_filtered += 1
                continue

            # 解析比分
            home_score, away_score = parse_score(score_str)

            # 创建或获取对手球队
            opponent_team = get_or_create_team(db, opponent_name)

            # 检查比赛是否已存在
            existing_match = db.query(Match).filter(
                Match.home_team_id == home_team.id,
                Match.away_team_id == opponent_team.id,
                Match.match_date == match_date
            ).first()

            if existing_match:
                matches_skipped += 1
                if matches_skipped <= 3:  # 只显示前 3 个跳过的
                    print(f"   ⏭️  已存在: {match_date.strftime('%Y-%m-%d')} vs {opponent_name}")
                match = existing_match
            else:
                # 创建比赛
                match = Match(
                    home_team_id=home_team.id,
                    away_team_id=opponent_team.id,
                    match_type=MatchType.FRIENDLY,
                    match_date=match_date,
                    venue="未知",  # Excel 中没有场地信息
                    home_score=home_score,
                    away_score=away_score,
                    status=MatchStatus.COMPLETED if home_score is not None else MatchStatus.SCHEDULED,
                    notes=f"从 my_football_data.xlsx 导入"
                )
                db.add(match)
                db.commit()
                db.refresh(match)
                matches_created += 1
                print(f"   ✅ {match_date.strftime('%Y-%m-%d')} vs {opponent_name} ({score_str})")

            # 创建球员比赛统计
            for player_name in player_names:
                # 获取该球员的进球和助攻列名
                goals_col = player_name
                assists_col = df.columns[df.columns.get_loc(player_name) + 1]

                # 获取进球和助攻数
                goals_value = row[goals_col]
                assists_value = row[assists_col]

                # 如果进球或助攻有值，说明该球员出勤了
                if pd.notna(goals_value) or pd.notna(assists_value):
                    player = players[player_name]

                    # 检查统计记录是否已存在
                    existing_stats = db.query(MatchPlayer).filter(
                        MatchPlayer.match_id == match.id,
                        MatchPlayer.player_id == player.id
                    ).first()

                    if not existing_stats:
                        # 转换进球和助攻数
                        goals = int(goals_value) if pd.notna(goals_value) and str(goals_value).strip() != '' else 0
                        assists = int(assists_value) if pd.notna(assists_value) and str(assists_value).strip() != '' else 0

                        # 创建球员比赛统计
                        match_player = MatchPlayer(
                            match_id=match.id,
                            player_id=player.id,
                            team_id=home_team.id,
                            played=True,
                            goals=goals,
                            assists=assists,
                            minutes_played=None  # Excel 中没有出场时间数据
                        )
                        db.add(match_player)
                        db.commit()
                        match_stats_created += 1

        if matches_skipped > 3:
            print(f"   ⏭️  还有 {matches_skipped - 3} 场比赛已存在...")

        if matches_2024_filtered > 0:
            print(f"   🔍 已过滤 {matches_2024_filtered} 场非 2025 年的比赛")

        # 统计信息
        print("\n" + "=" * 70)
        print("🎉 导入完成！")
        print(f"   📊 新增比赛: {matches_created} 场")
        print(f"   ⏭️  跳过比赛: {matches_skipped} 场（已存在）")
        print(f"   🔍 过滤非2025年: {matches_2024_filtered} 场")
        print(f"   ⚽ 新增球员统计: {match_stats_created} 条")
        print(f"   🏢 球队总数: {db.query(Team).count()}")
        print(f"   👥 球员总数: {db.query(Player).filter(Player.team_id == home_team.id).count()}")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        if db:
            db.rollback()
        sys.exit(1)
    finally:
        if db:
            db.close()


def get_or_create_team(db: Session, team_name: str, founded_year: int = None) -> Team:
    """获取或创建球队"""
    team = db.query(Team).filter(Team.name == team_name).first()
    if not team:
        team = Team(
            name=team_name,
            description=f"梅州客家队 - {team_name}",
            founded_year=founded_year
        )
        db.add(team)
        db.commit()
        db.refresh(team)
        print(f"      ✅ 创建球队: {team_name}")
    else:
        print(f"      💡 球队已存在: {team_name}")
    return team


def get_or_create_player(db: Session, team: Team, player_name: str, jersey_number: int = None) -> Player:
    """获取或创建球员"""
    # 先按名字查找
    player = db.query(Player).filter(
        Player.team_id == team.id,
        Player.name == player_name
    ).first()

    if not player:
        # position 字段是必需的，默认设置为"中场"
        player = Player(
            team_id=team.id,
            name=player_name,
            position="中场",  # 默认位置，可以在导入后修改
            jersey_number=jersey_number
        )
        db.add(player)
        db.commit()
        db.refresh(player)
        print(f"         ✅ {player_name}")
    else:
        print(f"         💡 {player_name} (已存在)")

    return player


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="导入梅州客家队 2025 年数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 干运行模式（查看数据但不导入）
  python import_2025_data.py --dry-run

  # 正式导入
  python import_2025_data.py

  # 指定自定义参数
  python import_2025_data.py --file data.xlsx --team 我的球队
        """
    )

    parser.add_argument("--file", default="my_football_data.xlsx", help="Excel 文件路径（默认：my_football_data.xlsx）")
    parser.add_argument("--team", default="梅州客家队", help="主队名称（默认：梅州客家队）")
    parser.add_argument("--dry-run", action="store_true", help="干运行模式：只读取数据不实际导入")

    args = parser.parse_args()

    import_2025_football_data(args.file, args.team, args.dry_run)
