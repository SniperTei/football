"""
简化的API测试 - 只测试核心功能
"""
import pytest
from fastapi.testclient import TestClient


class TestBasicAuth:
    """基础认证测试"""

    def test_login_success(self, client: TestClient, test_users, db):
        """测试成功登录"""
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]

    def test_login_wrong_password(self, client: TestClient, test_users, db):
        """测试错误密码"""
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200


class TestBasicTeams:
    """基础球队测试"""

    def test_get_teams(self, client: TestClient, test_teams, db):
        """测试获取球队列表"""
        response = client.get("/api/teams")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) == 2

    def test_get_team_by_id(self, client: TestClient, test_teams, db):
        """测试获取球队详情"""
        team_id = test_teams[0].id
        response = client.get(f"/api/teams/{team_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "曼联"

    def test_create_team_with_auth(self, client: TestClient, user_token, db):
        """测试创建球队（需要认证）"""
        response = client.post(
            "/api/teams",
            json={
                "name": "切尔西",
                "description": "切尔西足球俱乐部",
                "founded_year": 1905
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        # 创建成功应该返回201
        assert response.status_code in [200, 201]
        data = response.json()
        if response.status_code == 200:
            assert data["code"] == 200

    def test_delete_team_no_auth(self, client: TestClient, db):
        """测试未认证删除球队"""
        response = client.delete("/api/teams/1")
        # FastAPI默认返回403（不是401）
        assert response.status_code in [401, 403]


class TestBasicPlayers:
    """基础球员测试"""

    def test_get_players_empty(self, client: TestClient, db):
        """测试获取空球员列表"""
        response = client.get("/api/players")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) == 0

    def test_create_player_with_auth(self, client: TestClient, user_token, test_teams, db):
        """测试创建球员（需要认证）"""
        response = client.post(
            "/api/players",
            json={
                "name": "梅西",
                "position": "前锋",
                "jersey_number": 10,
                "team_id": test_teams[0].id
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 201]

    def test_create_player_no_auth(self, client: TestClient, db):
        """测试未认证创建球员"""
        response = client.post("/api/players", json={
            "name": "梅西",
            "position": "前锋",
            "jersey_number": 10,
            "team_id": 1
        })
        assert response.status_code in [401, 403]


class TestBasicPermissions:
    """基础权限测试"""

    def test_admin_can_delete_team(self, client: TestClient, admin_token, test_teams, db):
        """测试管理员可以删除球队"""
        team_id = test_teams[1].id  # 曼城
        response = client.delete(
            f"/api/teams/{team_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # 删除成功返回204
        assert response.status_code == 204

    def test_owner_can_delete_team(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试OWNER可以删除球队"""
        # user1是曼联的OWNER
        team_id = test_teams[0].id
        response = client.delete(
            f"/api/teams/{team_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204

    def test_admin_cannot_delete_team(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试ADMIN不能删除球队（只有OWNER能删除）"""
        # user1是曼城的ADMIN
        team_id = test_teams[1].id
        response = client.delete(
            f"/api/teams/{team_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        # 应该返回错误
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200
