"""
用户认证API测试
"""
import pytest
from fastapi.testclient import TestClient


class TestAuth:
    """用户认证测试"""

    def test_register_success(self, client: TestClient):
        """测试成功注册"""
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "password123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "注册成功"

    def test_register_duplicate_username(self, client: TestClient, test_users):
        """测试注册重复用户名"""
        response = client.post("/api/auth/register", json={
            "username": "admin",
            "email": "different@test.com",
            "password": "password123"
        })
        assert response.status_code in [200, 400]  # 接受200或400
        data = response.json()
        if response.status_code == 200:
            assert data["code"] != 200
            assert "已存在" in data["msg"]

    def test_register_duplicate_email(self, client: TestClient, test_users):
        """测试注册重复邮箱"""
        response = client.post("/api/auth/register", json={
            "username": "different",
            "email": "admin@test.com",
            "password": "password123"
        })
        assert response.status_code in [200, 400]
        data = response.json()
        if response.status_code == 200:
            assert data["code"] != 200
            assert "已存在" in data["msg"]

    def test_login_success(self, client: TestClient, test_users):
        """测试成功登录"""
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]
        assert "user" in data["data"]
        assert data["data"]["user"]["username"] == "admin"

    def test_login_wrong_username(self, client: TestClient):
        """测试错误的用户名"""
        response = client.post("/api/auth/login", json={
            "username": "wronguser",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200

    def test_login_wrong_password(self, client: TestClient, test_users):
        """测试错误的密码"""
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 200
        assert "用户名或密码错误" in data["msg"]

    def test_get_current_user(self, client: TestClient, admin_token):
        """测试获取当前用户信息"""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["username"] == "admin"

    def test_get_current_user_no_token(self, client: TestClient):
        """测试未登录获取当前用户"""
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """测试无效token获取当前用户"""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
