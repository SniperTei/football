"""
初始化数据库脚本
创建数据库表并插入初始数据
"""
from app.core.database import engine, Base, SessionLocal
from app.models import User, Team, TeamMember
from app.models.team_member import PermissionLevel
from app.core.security import get_password_hash


def init_db():
    """初始化数据库"""

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建成功")

    db = SessionLocal()

    try:
        # 检查是否已有数据
        if db.query(User).first():
            print("⚠ 数据库已有数据，跳过初始化")
            return

        # 创建默认管理员用户
        admin_user = User(
            username="admin",
            email="admin@football.com",
            hashed_password=get_password_hash("admin123"),
            is_admin=True,
            is_active=True
        )
        db.add(admin_user)
        db.flush()
        print("✓ 创建管理员用户: admin / admin123")

        # 创建示例球队
        teams_data = [
            {"name": "曼联", "description": "曼彻斯特联足球俱乐部", "founded_year": 1878},
            {"name": "曼城", "description": "曼彻斯特城足球俱乐部", "founded_year": 1894},
            {"name": "切尔西", "description": "切尔西足球俱乐部", "founded_year": 1905},
            {"name": "阿森纳", "description": "阿森纳足球俱乐部", "founded_year": 1886},
            {"name": "利物浦", "description": "利物浦足球俱乐部", "founded_year": 1892},
            {"name": "巴塞罗那", "description": "巴塞罗那足球俱乐部", "founded_year": 1899},
            {"name": "皇家马德里", "description": "皇家马德里足球俱乐部", "founded_year": 1902},
            {"name": "拜仁慕尼黑", "description": "拜仁慕尼黑足球俱乐部", "founded_year": 1900},
        ]

        teams = []
        for team_data in teams_data:
            team = Team(**team_data)
            db.add(team)
            db.flush()
            teams.append(team)
        print(f"✓ 创建 {len(teams)} 支球队")

        # 创建测试用户
        test_users = [
            {"username": "user1", "email": "user1@football.com", "password": "user123"},
            {"username": "user2", "email": "user2@football.com", "password": "user123"},
            {"username": "user3", "email": "user3@football.com", "password": "user123"},
        ]

        test_users_created = []
        for user_data in test_users:
            test_user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                is_admin=False,
                is_active=True
            )
            db.add(test_user)
            db.flush()
            test_users_created.append(test_user)
        print(f"✓ 创建 {len(test_users_created)} 个测试用户")

        # 分配球队权限
        team_members_data = [
            {"user_id": test_users_created[0].id, "team_id": teams[0].id, "permission": PermissionLevel.OWNER},
            {"user_id": test_users_created[0].id, "team_id": teams[1].id, "permission": PermissionLevel.ADMIN},
            {"user_id": test_users_created[1].id, "team_id": teams[1].id, "permission": PermissionLevel.MEMBER},
            {"user_id": test_users_created[1].id, "team_id": teams[2].id, "permission": PermissionLevel.MEMBER},
            {"user_id": test_users_created[2].id, "team_id": teams[3].id, "permission": PermissionLevel.OWNER},
            {"user_id": test_users_created[2].id, "team_id": teams[4].id, "permission": PermissionLevel.ADMIN},
        ]

        for member_data in team_members_data:
            member = TeamMember(**member_data)
            db.add(member)
        print(f"✓ 创建 {len(team_members_data)} 个球队成员权限")

        db.commit()
        print("\n✅ 数据库初始化完成！")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("开始初始化数据库...\n")
    init_db()
