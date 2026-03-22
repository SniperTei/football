"""
从 JSON 文件导入比赛数据到数据库
使用方法: python import_match_data.py
"""
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import Team, Player, Match, MatchPlayer
from app.models.match import MatchType, MatchStatus


def load_json_data():
    """加载 JSON 数据"""
    import json

    with open('2024_match_data.json', 'r', encoding='utf-8') as f:
        data_2024 = json.load(f)

    with open('2025_match_data.json', 'r', encoding='utf-8') as f:
        data_2025 = json.load(f)

    return data_2024['matches'] + data_2025['matches']


def create_teams(db: Session, matches):
    """创建球队"""
    print("\n=== 创建球队 ===")

    # 获取梅州客家队（应该已经在初始化时创建）
    our_team = db.query(Team).filter(Team.name == "梅州客家队").first()
    if not our_team:
        print("❌ 错误: 梅州客家队不存在！")
        print("请确保先启动服务器以初始化数据库（会自动创建梅州客家队）")
        raise Exception("梅州客家队不存在，请先运行数据库初始化")

    print(f"✅ 主队: {our_team.name} (ID: {our_team.id})")

    # 收集所有对手球队
    opponents = set()
    for match in matches:
        if match.get('opponent'):
            opponents.add(match['opponent'])

    # 创建对手球队
    opponent_teams = {}
    for opponent_name in sorted(opponents):
        team = db.query(Team).filter(Team.name == opponent_name).first()
        if not team:
            team = Team(
                name=opponent_name,
                description=f"对手球队: {opponent_name}"
            )
            db.add(team)
            db.flush()
            print(f"✅ 创建对手球队: {team.name} (ID: {team.id})")
        else:
            print(f"✅ 对手球队已存在: {team.name} (ID: {team.id})")

        opponent_teams[opponent_name] = team.id

    db.commit()

    return our_team.id, opponent_teams


def create_players(db: Session, matches, our_team_id):
    """创建球员"""
    print("\n=== 创建球员 ===")

    # 收集所有球员
    all_players = set()
    for match in matches:
        if match.get('attendance'):
            all_players.update(match['attendance'])
        if match.get('player_stats'):
            all_players.update(match['player_stats'].keys())

    # 为每个球员创建记录
    player_ids = {}
    for player_name in sorted(all_players):
        player = db.query(Player).filter(
            Player.name == player_name,
            Player.team_id == our_team_id
        ).first()

        if not player:
            player = Player(
                team_id=our_team_id,
                name=player_name,
                position="未知",  # 默认位置，后续可以修改
                jersey_number=None
            )
            db.add(player)
            db.flush()
            print(f"✅ 创建球员: {player.name} (ID: {player.id})")
        else:
            print(f"✅ 球员已存在: {player.name} (ID: {player.id})")

        player_ids[player_name] = player.id

    db.commit()

    return player_ids


def import_matches(db: Session, matches, our_team_id, opponent_teams, player_ids):
    """导入比赛数据和球员统计"""
    print("\n=== 导入比赛数据 ===")

    match_count = 0
    player_stats_count = 0

    for match_data in matches:
        try:
            # 解析日期
            match_date = datetime.strptime(match_data['date'], '%Y-%m-%d')

            # 获取对手球队ID
            opponent_name = match_data['opponent']
            away_team_id = opponent_teams.get(opponent_name)

            if not away_team_id:
                print(f"⚠️  跳过比赛: 找不到对手球队 {opponent_name}")
                continue

            # 检查比赛是否已存在
            existing_match = db.query(Match).filter(
                Match.home_team_id == our_team_id,
                Match.away_team_id == away_team_id,
                Match.match_date == match_date
            ).first()

            if existing_match:
                print(f"⚠️  比赛已存在，跳过: {match_data['date']} vs {opponent_name}")
                continue

            # 创建比赛记录
            match = Match(
                home_team_id=our_team_id,
                away_team_id=away_team_id,
                match_type=MatchType.FRIENDLY,
                match_date=match_date,
                home_score=match_data['score']['home'] if match_data.get('score') else None,
                away_score=match_data['score']['away'] if match_data.get('score') else None,
                status=MatchStatus.COMPLETED,
                notes=f"数据来源: JSON导入"
            )
            db.add(match)
            db.flush()

            print(f"✅ 创建比赛: {match_data['date']} vs {opponent_name} ({match_data['score']['home']}:{match_data['score']['away']})")
            match_count += 1

            # 导入球员统计
            attendance_set = set(match_data.get('attendance', []))
            player_stats_data = match_data.get('player_stats', {})

            # 1. 先处理有统计数据的球员
            for player_name, stats in player_stats_data.items():
                player_id = player_ids.get(player_name)
                if not player_id:
                    continue

                match_player = MatchPlayer(
                    match_id=match.id,
                    player_id=player_id,
                    team_id=our_team_id,
                    played=True,
                    goals=stats.get('goals', 0),
                    assists=stats.get('assists', 0)
                )
                db.add(match_player)
                player_stats_count += 1

            # 2. 处理出勤但无统计数据的球员
            for player_name in attendance_set:
                if player_name in player_stats_data:
                    continue  # 已经处理过了

                player_id = player_ids.get(player_name)
                if not player_id:
                    continue

                match_player = MatchPlayer(
                    match_id=match.id,
                    player_id=player_id,
                    team_id=our_team_id,
                    played=True,
                    goals=0,
                    assists=0
                )
                db.add(match_player)
                player_stats_count += 1

            # 每10场比赛提交一次，避免内存问题
            if match_count % 10 == 0:
                db.commit()

        except Exception as e:
            print(f"❌ 导入比赛失败: {match_data.get('date', 'Unknown')} - {e}")
            db.rollback()
            continue

    db.commit()

    print(f"\n✅ 导入完成:")
    print(f"   - 比赛场数: {match_count}")
    print(f"   - 球员统计记录: {player_stats_count}")


def main():
    """主函数"""
    print("="*60)
    print("开始导入比赛数据")
    print("="*60)

    try:
        # 加载JSON数据
        print("\n加载 JSON 文件...")
        matches = load_json_data()
        print(f"✅ 成功加载 {len(matches)} 场比赛")

        # 创建数据库会话
        db = SessionLocal()

        try:
            # 1. 创建球队
            our_team_id, opponent_teams = create_teams(db, matches)

            # 2. 创建球员
            player_ids = create_players(db, matches, our_team_id)

            # 3. 导入比赛数据
            import_matches(db, matches, our_team_id, opponent_teams, player_ids)

            print("\n" + "="*60)
            print("🎉 数据导入完成！")
            print("="*60)

        finally:
            db.close()

    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
