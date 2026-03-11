"""
球队API测试
"""
import pytest
from fastapi.testclient import TestClient


class TestTeams:
    """球队API测试"""

    def test_get_teams(self, client: TestClient, test_teams):
        """测试获取球队列表"""
        response = client.get("/api/teams")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) == 2
        assert data["data"]["list"][0]["name"] == "曼联"

    def test_get_team_by_id(self, client: TestClient, test_teams):
        """测试获取球队详情"""
        team_id = test_teams[0].id
        response = client.get(f"/api/teams/{team_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "曼联"

    def test_get_team_not_found(self, client: TestClient):
        """测试获取不存在的球队"""
        response = client.get("/api/teams/99999")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200

    def test_create_team_unauthorized(self, client: TestClient):
        """测试未登录创建球队"""
        response = client.post("/api/teams", json={
            "name": "切尔西",
            "description": "切尔西足球俱乐部",
            "founded_year": 1905
        })
        assert response.status_code == 401

    def test_create_team_success(self, client: TestClient, user_token):
        """测试成功创建球队"""
        response = client.post(
            "/api/teams",
            json={
                "name": "切尔西",
                "description": "切尔西足球俱乐部",
                "founded_year": 1905
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "切尔西"

    def test_create_team_duplicate_name(self, client: TestClient, user_token, test_teams):
        """测试创建重复名称的球队"""
        response = client.post(
            "/api/teams",
            json={
                "name": "曼联",
                "description": "另一个曼联",
                "founded_year": 2020
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200

    def test_update_team_unauthorized(self, client: TestClient, test_teams):
        """测试未登录更新球队"""
        team_id = test_teams[0].id
        response = client.put(f"/api/teams/{team_id}", json={
            "description": "更新后的描述"
        })
        assert response.status_code == 401

    def test_update_team_success(self, client: TestClient, user_token, test_teams, test_team_members):
        """测试成功更新球队（user1是曼联的OWNER）"""
        team_id = test_teams[0].id  # 曼联，user1是OWNER
        response = client.put(
            f"/api/teams/{team_id}",
            json={"description": "更新后的描述"},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_delete_team_unauthorized(self, client: TestClient, test_teams):
        """测试未登录删除球队"""
        team_id = test_teams[0].id
        response = client.delete(f"/api/teams/{team_id}")
        assert response.status_code == 401

    def test_delete_team_success(self, client: TestClient, admin_token, test_teams):
        """测试管理员成功删除球队"""
        team_id = test_teams[1].id  # 曼城
        response = client.delete(
            f"/api/teams/{team_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204

    def test_delete_team_no_permission(self, client: TestClient, user_token, test_teams, test_team_members):
        """测试无权限删除球队（user2不是OWNER）"""
        # user_token是user1，他有曼城的ADMIN权限，不能删除
        # 但他是曼联的OWNER，可以删除曼联
        team_id = test_teams[1].id  # 曼城，user1是ADMIN
        response = client.delete(
            f"/api/teams/{team_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200
        assert "权限" in data["msg"]
