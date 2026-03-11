"""
球员API测试
"""
import pytest
from fastapi.testclient import TestClient
from app.models.player import Player


class TestPlayers:
    """球员API测试"""

    def test_get_players_empty(self, client: TestClient):
        """测试获取空球员列表"""
        response = client.get("/api/players")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) == 0

    def test_create_player_unauthorized(self, client: TestClient, test_teams):
        """测试未登录创建球员"""
        response = client.post("/api/players", json={
            "name": "梅西",
            "position": "前锋",
            "jersey_number": 10,
            "team_id": test_teams[0].id
        })
        assert response.status_code == 401

    def test_create_player_success(self, client: TestClient, user_token, test_teams):
        """测试成功创建球员"""
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
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "梅西"

    def test_create_player_no_permission(self, client: TestClient, db, test_teams):
        """测试无权限创建球员"""
        # 创建一个没有权限的用户
        from app.core.security import get_password_hash
        from app.models import User
        user = User(
            username="noperm",
            email="noperm@test.com",
            hashed_password=get_password_hash("test123"),
            is_admin=False,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # 登录获取token
        response = client.post("/api/auth/login", json={
            "username": "noperm",
            "password": "test123"
        })
        token = response.json()["data"]["access_token"]

        # 尝试创建球员（该用户对球队没有任何权限）
        response = client.post(
            "/api/players",
            json={
                "name": "测试球员",
                "position": "前锋",
                "jersey_number": 1,
                "team_id": test_teams[0].id
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200
        assert "权限" in data["msg"]

    def test_get_players_by_team(self, client: TestClient, user_token, test_teams):
        """测试获取指定球队的球员"""
        # 先创建几个球员
        client.post(
            "/api/players",
            json={
                "name": "梅西",
                "position": "前锋",
                "jersey_number": 10,
                "team_id": test_teams[0].id
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        client.post(
            "/api/players",
            json={
                "name": "C罗",
                "position": "前锋",
                "jersey_number": 7,
                "team_id": test_teams[0].id
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )

        response = client.get(f"/api/players/team/{test_teams[0].id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) == 2

    def test_update_player_success(self, client: TestClient, user_token, test_teams):
        """测试成功更新球员"""
        # 先创建球员
        create_response = client.post(
            "/api/players",
            json={
                "name": "梅西",
                "position": "前锋",
                "jersey_number": 10,
                "team_id": test_teams[0].id
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        player_id = create_response.json()["data"]["id"]

        # 更新球员
        response = client.put(
            f"/api/players/{player_id}",
            json={"name": "里奥·梅西"},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "里奥·梅西"

    def test_delete_player_success(self, client: TestClient, user_token, test_teams):
        """测试成功删除球员"""
        # 先创建球员
        create_response = client.post(
            "/api/players",
            json={
                "name": "测试球员",
                "position": "前锋",
                "jersey_number": 1,
                "team_id": test_teams[0].id
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        player_id = create_response.json()["data"]["id"]

        # 删除球员
        response = client.delete(
            f"/api/players/{player_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204
