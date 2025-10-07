import pytest
from httpx import AsyncClient


class TestAuth:
    """Test authentication endpoints"""

    async def test_login_success(self, test_client: AsyncClient, test_admin_user):
        """Test successful login"""
        response = await test_client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, test_client: AsyncClient, test_admin_user):
        """Test login with invalid credentials"""
        response = await test_client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    async def test_login_nonexistent_user(self, test_client: AsyncClient):
        """Test login with non-existent user"""
        response = await test_client.post("/api/v1/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "password"
        })

        assert response.status_code == 401

    async def test_get_current_user(self, test_client: AsyncClient, admin_auth_headers):
        """Test getting current user info"""
        response = await test_client.get("/api/v1/auth/me", headers=admin_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"

    async def test_protected_endpoint_without_auth(self, test_client: AsyncClient):
        """Test accessing protected endpoint without authentication"""
        response = await test_client.get("/api/v1/auth/me")

        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    async def test_protected_endpoint_invalid_token(self, test_client: AsyncClient):
        """Test accessing protected endpoint with invalid token"""
        response = await test_client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid_token"
        })

        assert response.status_code == 401

    async def test_refresh_token(self, test_client: AsyncClient, test_admin_user):
        """Test token refresh"""
        # First, login to get tokens
        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        tokens = login_response.json()

        # Use refresh token to get new access token
        refresh_response = await test_client.post("/api/v1/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })

        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens

    async def test_change_password(self, test_client: AsyncClient, admin_auth_headers):
        """Test password change"""
        response = await test_client.post("/api/v1/auth/change-password",
            headers=admin_auth_headers,
            json={
                "current_password": "admin123",
                "new_password": "newpassword123"
            }
        )

        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]

    async def test_change_password_wrong_current(self, test_client: AsyncClient, admin_auth_headers):
        """Test password change with wrong current password"""
        response = await test_client.post("/api/v1/auth/change-password",
            headers=admin_auth_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123"
            }
        )

        assert response.status_code == 401
        assert "Current password is incorrect" in response.json()["detail"]