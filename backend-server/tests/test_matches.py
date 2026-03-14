"""
比赛相关API测试
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone


class TestMatchCreation:
    """比赛创建测试"""

    def test_create_match_with_new_opponent(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试创建比赛（对手球队不存在，自动创建）"""
        from datetime import datetime, timedelta, timezone

        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        response = client.post(
            "/api/matches",
            json={
                "away_team_name": "巴塞罗那",
                "match_type": "friendly",
                "match_date": match_date,
                "venue": "老特拉福德球场"
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["away_team_name"] == "巴塞罗那"

    def test_create_match_with_existing_opponent(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试创建比赛（对手球队已存在）"""
        match_date = (datetime.now(timezone.utc) + timedelta(days=-2)).isoformat()
        response = client.post(
            "/api/matches",
            json={
                "away_team_name": test_teams[1].name,  # 曼城已存在
                "match_type": "league",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["away_team_id"] == test_teams[1].id

    def test_create_match_no_auth(self, client: TestClient, test_teams, db):
        """测试未认证创建比赛"""
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        response = client.post(
            "/api/matches",
            json={
                "away_team_name": "AC米兰",
                "match_type": "friendly",
                "match_date": match_date
            }
        )
        assert response.status_code in [401, 403]

    def test_create_match_same_team(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试不能和同一支球队比赛"""
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        response = client.post(
            "/api/matches",
            json={
                "away_team_name": test_teams[0].name,  # 同一支球队
                "match_type": "friendly",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        # 创建失败是预期的，因为主队和客队不能相同
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["code"] != 200  # 应该返回错误


class TestMatchRetrieval:
    """比赛查询测试"""

    def test_get_match_by_id(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试获取比赛详情"""
        # 先创建一场比赛
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        create_response = client.post(
            "/api/matches",
            json={
                "away_team_name": "利物浦",
                "match_type": "friendly",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        match_id = create_response.json()["data"]["id"]

        # 获取比赛详情
        response = client.get(
            f"/api/matches/{match_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["home_team_name"] == test_teams[0].name

    def test_get_team_matches(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试获取球队的所有比赛"""
        # 创建两场比赛
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        client.post(
            "/api/matches",
            json={
                "away_team_name": "阿森纳",
                "match_type": "friendly",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )

        response = client.get(
            f"/api/matches/team/{test_teams[0].id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) >= 1

    def test_get_upcoming_matches(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试获取未来比赛"""
        match_date = (datetime.now(timezone.utc) + timedelta(days=-5)).isoformat()
        client.post(
            "/api/matches",
            json={
                "away_team_name": "拜仁慕尼黑",
                "match_type": "league",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )

        response = client.get(
            f"/api/matches/upcoming/{test_teams[0].id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestMatchUpdate:
    """比赛更新测试"""

    def test_update_match_score(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试更新比赛比分"""
        # 先创建比赛
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        create_response = client.post(
            "/api/matches",
            json={
                "away_team_name": "尤文图斯",
                "match_type": "friendly",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        match_id = create_response.json()["data"]["id"]

        # 更新比分
        response = client.put(
            f"/api/matches/{match_id}",
            json={
                "home_score": 2,
                "away_score": 1
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["home_score"] == 2
        assert data["data"]["away_score"] == 1
        assert data["data"]["status"] == "completed"  # 自动更新状态

    def test_update_match_no_permission(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试无权限更新比赛"""
        # 创建曼联的比赛（user1是owner）
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        create_response = client.post(
            "/api/matches",
            json={
                "away_team_name": "国际米兰",
                "match_type": "friendly",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}  # user1是曼联的owner
        )

        # user2对曼城没有权限，不能修改曼联的比赛
        from app.models.user import User
        user2 = db.query(User).filter(User.username == "user2").first()
        token = self._login_as_user(client, user2.username, "user123")

        match_id = create_response.json()["data"]["id"]
        response = client.put(
            f"/api/matches/{match_id}",
            json={"home_score": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200  # 应该返回错误

    def _login_as_user(self, client, username, password):
        """辅助方法：登录获取token"""
        response = client.post("/api/auth/login", json={
            "username": username,
            "password": password
        })
        return response.json()["data"]["access_token"]


class TestMatchDeletion:
    """比赛删除测试"""

    def test_delete_match_with_permission(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试有权限删除比赛"""
        # 创建比赛
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        create_response = client.post(
            "/api/matches",
            json={
                "away_team_name": "多特蒙德",
                "match_type": "friendly",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        match_id = create_response.json()["data"]["id"]

        # 删除比赛（user1是曼联的OWNER，有权限）
        response = client.delete(
            f"/api/matches/{match_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_delete_match_no_permission(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试无权限删除比赛（需要ADMIN权限）"""
        # 创建曼联的比赛
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        create_response = client.post(
            "/api/matches",
            json={
                "away_team_name": "罗马",
                "match_type": "friendly",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        match_id = create_response.json()["data"]["id"]

        # user2对曼联没有权限
        from app.models.user import User
        user2 = db.query(User).filter(User.username == "user2").first()
        token = self._login_as_user(client, user2.username, "user123")

        response = client.delete(
            f"/api/matches/{match_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200  # 应该返回错误

    def _login_as_user(self, client, username, password):
        """辅助方法：登录获取token"""
        response = client.post("/api/auth/login", json={
            "username": username,
            "password": password
        })
        return response.json()["data"]["access_token"]
