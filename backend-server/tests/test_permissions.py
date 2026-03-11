"""
权限系统测试
"""
import pytest
from fastapi.testclient import TestClient


class TestPermissions:
    """权限系统测试"""

    def test_admin_can_do_anything(self, client: TestClient, admin_token, test_teams):
        """测试管理员可以做任何操作"""
        # 创建球队
        response = client.post(
            "/api/teams",
            json={
                "name": "新球队",
                "description": "管理员创建的球队"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        team_id = response.json()["data"]["id"]

        # 删除球队
        response = client.delete(
            f"/api/teams/{team_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204

    def test_owner_can_delete_team(self, client: TestClient, user_token, test_teams, test_team_members):
        """测试OWNER可以删除球队"""
        # user1是曼联的OWNER
        team_id = test_teams[0].id
        response = client.delete(
            f"/api/teams/{team_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 204

    def test_admin_cannot_delete_team(self, client: TestClient, user_token, test_teams, test_team_members):
        """测试ADMIN不能删除球队"""
        # user1是曼城的ADMIN，不能删除
        team_id = test_teams[1].id
        response = client.delete(
            f"/api/teams/{team_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200
        assert "权限" in data["msg"]

    def test_member_cannot_delete_team(self, client: TestClient, db, test_teams, test_team_members):
        """测试MEMBER不能删除球队"""
        # 获取user2的token（user2是曼城的MEMBER）
        from app.core.security import get_password_hash
        from app.models import User
        user = db.query(User).filter(User.username == "user2").first()

        response = client.post("/api/auth/login", json={
            "username": "user2",
            "password": "user123"
        })
        token = response.json()["data"]["access_token"]

        # user2尝试删除曼城
        team_id = test_teams[1].id
        response = client.delete(
            f"/api/teams/{team_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200

    def test_owner_can_create_player(self, client: TestClient, user_token, test_teams, test_team_members):
        """测试OWNER可以创建球员"""
        # user1是曼联的OWNER
        response = client.post(
            "/api/players",
            json={
                "name": "C罗",
                "position": "前锋",
                "jersey_number": 7,
                "team_id": test_teams[0].id
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_admin_can_create_player(self, client: TestClient, user_token, test_teams, test_team_members):
        """测试ADMIN可以创建球员"""
        # user1是曼城的ADMIN
        response = client.post(
            "/api/players",
            json={
                "name": "德布劳内",
                "position": "中场",
                "jersey_number": 17,
                "team_id": test_teams[1].id
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_member_cannot_create_player(self, client: TestClient, db, test_teams, test_team_members):
        """测试MEMBER不能创建球员"""
        # 获取user2的token（user2是曼城的MEMBER）
        from app.models import User
        user = db.query(User).filter(User.username == "user2").first()

        response = client.post("/api/auth/login", json={
            "username": "user2",
            "password": "user123"
        })
        token = response.json()["data"]["access_token"]

        # user2尝试为曼城创建球员
        response = client.post(
            "/api/players",
            json={
                "name": "测试球员",
                "position": "前锋",
                "jersey_number": 1,
                "team_id": test_teams[1].id
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200
        assert "权限" in data["msg"]
