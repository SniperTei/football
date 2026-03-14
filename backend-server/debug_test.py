"""
调试测试脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models import User, Team, TeamMember
from app.models.team_member import PermissionLevel
from app.core.security import get_password_hash

# 创建数据库会话
db = SessionLocal()

# 清理并创建测试数据
try:
    # 创建用户
    user = db.query(User).filter(User.username == "testuser").first()
    if not user:
        user = User(
            username="testuser",
            email="test@test.com",
            hashed_password=get_password_hash("test123"),
            is_admin=False,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 创建球队
    team = db.query(Team).filter(Team.name == "测试球队").first()
    if not team:
        team = Team(name="测试球队", description="测试")
        db.add(team)
        db.commit()
        db.refresh(team)

    # 分配权限
    existing_member = db.query(TeamMember).filter(
        TeamMember.user_id == user.id,
        TeamMember.team_id == team.id
    ).first()
    if not existing_member:
        member = TeamMember(
            user_id=user.id,
            team_id=team.id,
            permission=PermissionLevel.OWNER
        )
        db.add(member)
        db.commit()

    print(f"User ID: {user.id}")
    print(f"Team ID: {team.id}")

    # 创建测试客户端
    client = TestClient(app)

    # 登录
    login_response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "test123"
    })
    print(f"\nLogin response: {login_response.json()}")

    if login_response.status_code == 200:
        token = login_response.json()["data"]["access_token"]

        # 创建比赛
        match_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        print(f"\nMatch date: {match_date}")

        response = client.post(
            "/api/matches",
            json={
                "home_team_id": team.id,
                "away_team_name": "巴塞罗那",
                "match_type": "friendly",
                "match_date": match_date,
                "venue": "老特拉福德球场"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.json()}")

finally:
    db.close()
