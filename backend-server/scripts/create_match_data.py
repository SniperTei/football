"""
创建示例比赛数据
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import Team, Player, User, TeamMember, Match, MatchPlayer
from app.models.match import MatchType, MatchStatus
from app.models.team_member import PermissionLevel
from app.core.security import get_password_hash


def create_sample_data():
    """创建示例数据"""
    db: Session = SessionLocal()

    try:
        # 1. 检查现有数据
        print("检查现有数据...")
        teams = db.query(Team).all()
        users = db.query(User).all()

        if not teams:
            print("没有找到球队，先创建一些球队...")
            teams = [
                Team(name="曼联", description="曼彻斯特联足球俱乐部", founded_year=1878),
                Team(name="曼城", description="曼彻斯特城足球俱乐部", founded_year=1894),
                Team(name="利物浦", description="利物浦足球俱乐部", founded_year=1892),
                Team(name="切尔西", description="切尔西足球俱乐部", founded_year=1905),
                Team(name="阿森纳", description="阿森纳足球俱乐部", founded_year=1886),
            ]
            for team in teams:
                db.add(team)
            db.commit()
            for team in teams:
                db.refresh(team)
            print(f"创建了 {len(teams)} 个球队")
        else:
            print(f"找到 {len(teams)} 个球队")

        if not users:
            print("没有找到用户，创建测试用户...")
            admin = User(
                username="admin",
                email="admin@football.com",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

            # 为管理员添加球队权限
            for team in teams[:2]:
                team_member = TeamMember(
                    user_id=admin.id,
                    team_id=team.id,
                    permission=PermissionLevel.OWNER
                )
                db.add(team_member)
            db.commit()
            print("创建了管理员用户")
        else:
            print(f"找到 {len(users)} 个用户")

        # 刷新数据
        db.rollback()
        teams = db.query(Team).all()
        users = db.query(User).all()

        # 2. 为球队创建一些球员
        print("\n创建球员...")
        players_data = {
            "曼联": [
                {"name": "C罗", "position": "前锋", "jersey_number": 7},
                {"name": "B费", "position": "中场", "jersey_number": 8},
                {"name": "卡塞米罗", "position": "中场", "jersey_number": 18},
                {"name": "拉什福德", "position": "前锋", "jersey_number": 10},
                {"name": "德赫亚", "position": "门将", "jersey_number": 1},
            ],
            "曼城": [
                {"name": "德布劳内", "position": "中场", "jersey_number": 17},
                {"name": "哈兰德", "position": "前锋", "jersey_number": 9},
                {"name": "福登", "position": "中场", "jersey_number": 47},
            ],
            "利物浦": [
                {"name": "萨拉赫", "position": "前锋", "jersey_number": 11},
                {"name": "范戴克", "position": "后卫", "jersey_number": 4},
            ],
            "切尔西": [
                {"name": "帕尔默", "position": "中场", "jersey_number": 20},
                {"name": "杰克逊", "position": "前锋", "jersey_number": 15},
            ],
            "阿森纳": [
                {"name": "萨卡", "position": "前锋", "jersey_number": 7},
                {"name": "厄德高", "position": "中场", "jersey_number": 8},
            ],
        }

        all_players = {}
        for team in teams:
            if team.name in players_data:
                team_players = []
                for player_data in players_data[team.name]:
                    # 检查是否已存在
                    existing = db.query(Player).filter(
                        Player.name == player_data["name"],
                        Player.team_id == team.id
                    ).first()
                    if not existing:
                        player = Player(
                            name=player_data["name"],
                            position=player_data["position"],
                            jersey_number=player_data["jersey_number"],
                            team_id=team.id
                        )
                        db.add(player)
                        db.commit()
                        db.refresh(player)
                        team_players.append(player)
                    else:
                        team_players.append(existing)
                all_players[team.name] = team_players
                print(f"  {team.name}: {len(team_players)} 个球员")

        # 3. 创建比赛数据
        print("\n创建比赛...")
        now = datetime.now(timezone.utc)

        # 已完成的比赛
        completed_matches = [
            {
                "home": "曼联", "away": "利物浦",
                "home_score": 3, "away_score": 1,
                "date": now - timedelta(days=10),
                "type": MatchType.LEAGUE,
                "venue": "老特拉福德",
                "stats": {
                    "曼联": [
                        {"player": "C罗", "played": True, "goals": 2, "assists": 0},
                        {"player": "B费", "played": True, "goals": 0, "assists": 2},
                        {"player": "卡塞米罗", "played": True, "goals": 1, "assists": 0},
                        {"player": "拉什福德", "played": True, "goals": 0, "assists": 1},
                        {"player": "德赫亚", "played": True, "goals": 0, "assists": 0},
                    ],
                    "利物浦": [
                        {"player": "萨拉赫", "played": True, "goals": 1, "assists": 0},
                        {"player": "范戴克", "played": True, "goals": 0, "assists": 0},
                    ]
                }
            },
            {
                "home": "曼城", "away": "曼联",
                "home_score": 2, "away_score": 2,
                "date": now - timedelta(days=5),
                "type": MatchType.LEAGUE,
                "venue": "伊蒂哈德球场",
                "stats": {
                    "曼城": [
                        {"player": "德布劳内", "played": True, "goals": 1, "assists": 1},
                        {"player": "哈兰德", "played": True, "goals": 1, "assists": 0},
                        {"player": "福登", "played": True, "goals": 0, "assists": 0},
                    ],
                    "曼联": [
                        {"player": "C罗", "played": True, "goals": 1, "assists": 0},
                        {"player": "B费", "played": True, "goals": 1, "assists": 1},
                        {"player": "卡塞米罗", "played": False, "goals": 0, "assists": 0},
                        {"player": "拉什福德", "played": True, "goals": 0, "assists": 0},
                        {"player": "德赫亚", "played": True, "goals": 0, "assists": 0},
                    ]
                }
            },
            {
                "home": "切尔西", "away": "阿森纳",
                "home_score": 1, "away_score": 2,
                "date": now - timedelta(days=3),
                "type": MatchType.LEAGUE,
                "venue": "斯坦福桥",
                "stats": {
                    "切尔西": [
                        {"player": "帕尔默", "played": True, "goals": 1, "assists": 0},
                        {"player": "杰克逊", "played": True, "goals": 0, "assists": 0},
                    ],
                    "阿森纳": [
                        {"player": "萨卡", "played": True, "goals": 1, "assists": 1},
                        {"player": "厄德高", "played": True, "goals": 1, "assists": 0},
                    ]
                }
            },
        ]

        # 即将到来的比赛
        upcoming_matches = [
            {
                "home": "曼联", "away": "切尔西",
                "date": now + timedelta(days=2),
                "type": MatchType.LEAGUE,
                "venue": "老特拉福德",
            },
            {
                "home": "利物浦", "away": "曼城",
                "date": now + timedelta(days=5),
                "type": MatchType.FRIENDLY,
                "venue": "安菲尔德",
            },
            {
                "home": "阿森纳", "away": "曼联",
                "date": now + timedelta(days=7),
                "type": MatchType.LEAGUE,
                "venue": "酋长球场",
            },
        ]

        team_map = {team.name: team for team in teams}

        # 创建已完成的比赛
        for match_data in completed_matches:
            home_team = team_map[match_data["home"]]
            away_team = team_map[match_data["away"]]

            match = Match(
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                match_type=match_data["type"],
                match_date=match_data["date"],
                venue=match_data["venue"],
                home_score=match_data["home_score"],
                away_score=match_data["away_score"],
                status=MatchStatus.COMPLETED
            )
            db.add(match)
            db.commit()
            db.refresh(match)

            print(f"  创建比赛: {home_team.name} {match_data['home_score']} - {match_data['away_score']} {away_team.name}")

            # 创建球员统计
            for team_name, team_stats in match_data["stats"].items():
                for stat in team_stats:
                    # 找到球员
                    player = db.query(Player).filter(
                        Player.name == stat["player"],
                        Player.team_id == team_map[team_name].id
                    ).first()

                    if player:
                        match_player = MatchPlayer(
                            match_id=match.id,
                            player_id=player.id,
                            team_id=player.team_id,
                            played=stat["played"],
                            goals=stat["goals"],
                            assists=stat["assists"]
                        )
                        db.add(match_player)
            db.commit()

        # 创建即将到来的比赛
        for match_data in upcoming_matches:
            home_team = team_map[match_data["home"]]
            away_team = team_map[match_data["away"]]

            match = Match(
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                match_type=match_data["type"],
                match_date=match_data["date"],
                venue=match_data["venue"],
                status=MatchStatus.SCHEDULED
            )
            db.add(match)
            db.commit()
            db.refresh(match)

            print(f"  创建即将到来的比赛: {home_team.name} vs {away_team.name}")

            # 为主队球员初始化空记录
            if home_team.name in all_players:
                for player in all_players[home_team.name]:
                    match_player = MatchPlayer(
                        match_id=match.id,
                        player_id=player.id,
                        team_id=player.team_id,
                        played=False,
                        goals=0,
                        assists=0
                    )
                    db.add(match_player)
                db.commit()

        print("\n✅ 数据创建完成！")
        print(f"\n统计信息:")
        print(f"  - 球队数量: {len(teams)}")
        print(f"  - 比赛数量: {len(completed_matches) + len(upcoming_matches)}")
        print(f"  - 球员数量: {sum(len(players) for players in all_players.values())}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
