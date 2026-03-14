"""
比赛球员统计API测试
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone


class TestMatchPlayerStats:
    """比赛球员统计测试"""

    def test_update_player_stats(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试更新球员比赛统计"""
        # 先创建比赛
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        match_response = client.post(
            "/api/matches",
            json={
                "away_team_name": "热刺",
                "match_type": "friendly",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        match_id = match_response.json()["data"]["id"]

        # 创建一个球员
        player_response = client.post(
            "/api/players",
            json={
                "name": "C罗",
                "position": "前锋",
                "jersey_number": 7,
                "team_id": test_teams[0].id
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        player_id = player_response.json()["data"]["id"]

        # 更新球员统计
        response = client.put(
            f"/api/match-players/match/{match_id}/player/{player_id}",
            json={
                "played": True,
                "goals": 2,
                "assists": 1,
                "minutes_played": 90
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["goals"] == 2
        assert data["data"]["assists"] == 1

    def test_get_match_player_stats(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试获取比赛的所有球员统计"""
        # 创建比赛
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        match_response = client.post(
            "/api/matches",
            json={
                "away_team_name": "埃弗顿",
                "match_type": "league",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        match_id = match_response.json()["data"]["id"]

        # 创建比赛时应该自动初始化了球员记录
        response = client.get(
            f"/api/match-players/match/{match_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_update_player_stats_no_permission(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试无权限更新球员统计"""
        # 创建曼联的比赛
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        match_response = client.post(
            "/api/matches",
            json={
                "away_team_name": "西汉姆",
                "match_type": "friendly",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        match_id = match_response.json()["data"]["id"]

        # 创建球员
        player_response = client.post(
            "/api/players",
            json={
                "name": "B费",
                "position": "中场",
                "team_id": test_teams[0].id
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        player_id = player_response.json()["data"]["id"]

        # user2对曼联没有权限
        from app.models.user import User
        user2 = db.query(User).filter(User.username == "user2").first()
        token = self._login_as_user(client, user2.username, "user123")

        response = client.put(
            f"/api/match-players/match/{match_id}/player/{player_id}",
            json={"goals": 1},
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


class TestAttendanceRate:
    """出勤率测试"""

    def test_get_player_attendance_rate_no_matches(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试获取球员出勤率（没有比赛）"""
        # 创建球员
        player_response = client.post(
            "/api/players",
            json={
                "name": "拉什福德",
                "position": "前锋",
                "team_id": test_teams[0].id
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        player_id = player_response.json()["data"]["id"]

        response = client.get(
            f"/api/match-players/attendance/{test_teams[0].id}/player/{player_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["total_matches"] == 0
        assert data["data"]["attendance_rate"] == 0.0

    def test_get_player_attendance_rate_with_matches(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试获取球员出勤率（有比赛记录）"""
        from datetime import datetime, timedelta, timezone

        # 创建球员
        player_response = client.post(
            "/api/players",
            json={
                "name": "卡塞米罗",
                "position": "中场",
                "team_id": test_teams[0].id
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        player_id = player_response.json()["data"]["id"]

        # 创建2场已完成的比赛
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()

        # 第一场比赛
        match1_response = client.post(
            "/api/matches",
            json={
                "away_team_name": "纽卡斯尔",
                "match_type": "league",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        match1_id = match1_response.json()["data"]["id"]

        # 更新比分（状态变为completed）
        client.put(
            f"/api/matches/{match1_id}",
            json={"home_score": 3, "away_score": 1},
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # 球员出场
        client.put(
            f"/api/match-players/match/{match1_id}/player/{player_id}",
            json={"played": True, "goals": 1},
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # 第二场比赛
        match2_response = client.post(
            "/api/matches",
            json={
                "away_team_name": "维拉",
                "match_type": "league",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        match2_id = match2_response.json()["data"]["id"]

        # 更新比分
        client.put(
            f"/api/matches/{match2_id}",
            json={"home_score": 2, "away_score": 0},
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # 球员未出场
        client.put(
            f"/api/match-players/match/{match2_id}/player/{player_id}",
            json={"played": False},
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # 获取出勤率
        response = client.get(
            f"/api/match-players/attendance/{test_teams[0].id}/player/{player_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["total_matches"] == 2
        assert data["data"]["played_matches"] == 1
        assert data["data"]["attendance_rate"] == 50.0
        assert data["data"]["total_goals"] == 1

    def test_get_team_attendance_rates(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试获取球队所有球员的出勤率"""
        # 创建多个球员
        for name in ["德赫亚", "瓦拉内", "利桑德罗"]:
            client.post(
                "/api/players",
                json={
                    "name": name,
                    "position": "后卫",
                    "team_id": test_teams[0].id
                },
                headers={"Authorization": f"Bearer {user_token}"}
            )

        response = client.get(
            f"/api/match-players/attendance/{test_teams[0].id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) >= 3

    def test_attendance_rate_no_permission(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试查看出勤率（不需要权限）"""
        # user2对曼联没有权限
        from app.models.user import User
        user2 = db.query(User).filter(User.username == "user2").first()
        token = self._login_as_user(client, user2.username, "user123")

        response = client.get(
            f"/api/match-players/attendance/{test_teams[0].id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        # 现在查看出勤率不需要权限，任何登录用户都可以查看
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def _login_as_user(self, client, username, password):
        """辅助方法：登录获取token"""
        response = client.post("/api/auth/login", json={
            "username": username,
            "password": password
        })
        return response.json()["data"]["access_token"]


class TestMatchPlayerAutoInit:
    """测试比赛球员自动初始化"""

    def test_match_players_auto_initialized(self, client: TestClient, user_token, test_teams, test_team_members, db):
        """测试创建比赛时自动初始化球员记录"""
        # 先创建几个球员
        for i in range(3):
            client.post(
                "/api/players",
                json={
                    "name": f"球员{i}",
                    "position": "前锋",
                    "team_id": test_teams[0].id
                },
                headers={"Authorization": f"Bearer {user_token}"}
            )

        # 创建比赛
        match_date = (datetime.now(timezone.utc) + timedelta(days=-1)).isoformat()
        match_response = client.post(
            "/api/matches",
            json={
                "away_team_name": "富勒姆",
                "match_type": "friendly",
                "match_date": match_date
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        match_id = match_response.json()["data"]["id"]

        # 检查是否自动创建了球员记录
        response = client.get(
            f"/api/match-players/match/{match_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 应该有至少3个球员记录
        assert len(data["data"]["list"]) >= 3

        # 检查初始状态
        for player_stat in data["data"]["list"]:
            if player_stat["team_id"] == test_teams[0].id:
                # 主队球员默认played=False
                assert player_stat["played"] == False
                assert player_stat["goals"] == 0
                assert player_stat["assists"] == 0
