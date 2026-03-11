"""
pytest配置文件
提供测试fixtures和测试客户端
"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from main import app
from app.core.security import get_password_hash
from app.models import User, Team, TeamMember, Player
from app.models.player import Player as PlayerModel
from app.models.team_member import PermissionLevel

# 使用内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # 使用静态连接池
    pool_pre_ping=True,
    echo=False
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def db():
    """创建测试数据库（autouse确保在所有需要数据库的测试之前执行）"""
    # 导入所有模型以确保表被创建
    from app.models.user import User as UserModel
    from app.models.team import Team as TeamModel
    from app.models.team_member import TeamMember as TeamMemberModel
    from app.models.player import Player as PlayerModel

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        # 清理所有表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_users(db):
    """创建测试用户"""
    users = [
        User(
            username="admin",
            email="admin@test.com",
            hashed_password=get_password_hash("admin123"),
            is_admin=True,
            is_active=True
        ),
        User(
            username="user1",
            email="user1@test.com",
            hashed_password=get_password_hash("user123"),
            is_admin=False,
            is_active=True
        ),
        User(
            username="user2",
            email="user2@test.com",
            hashed_password=get_password_hash("user123"),
            is_admin=False,
            is_active=True
        ),
    ]
    for user in users:
        db.add(user)
    db.commit()
    for user in users:
        db.refresh(user)
    return users


@pytest.fixture
def test_teams(db):
    """创建测试球队"""
    teams = [
        Team(name="曼联", description="曼彻斯特联足球俱乐部", founded_year=1878),
        Team(name="曼城", description="曼彻斯特城足球俱乐部", founded_year=1894),
    ]
    for team in teams:
        db.add(team)
    db.commit()
    for team in teams:
        db.refresh(team)
    return teams


@pytest.fixture
def test_team_members(db, test_users, test_teams):
    """创建测试球队成员"""
    team_members = [
        TeamMember(
            user_id=test_users[1].id,
            team_id=test_teams[0].id,
            permission=PermissionLevel.OWNER
        ),
        TeamMember(
            user_id=test_users[1].id,
            team_id=test_teams[1].id,
            permission=PermissionLevel.ADMIN
        ),
        TeamMember(
            user_id=test_users[2].id,
            team_id=test_teams[1].id,
            permission=PermissionLevel.MEMBER
        ),
    ]
    for member in team_members:
        db.add(member)
    db.commit()
    return team_members


@pytest.fixture
def admin_token(client, test_users):
    """获取管理员token"""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["data"]["access_token"]


@pytest.fixture
def user_token(client, test_users):
    """获取普通用户token"""
    response = client.post("/api/auth/login", json={
        "username": "user1",
        "password": "user123"
    })
    return response.json()["data"]["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    """获取认证头"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_auth_headers(user_token):
    """获取普通用户认证头"""
    return {"Authorization": f"Bearer {user_token}"}
