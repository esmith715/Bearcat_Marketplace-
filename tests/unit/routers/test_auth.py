import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from server.main import app


#=========================#
# POST /auth/verify-email #
#=========================#

class TestVerifyEmail:

    
    async def test_verify_email_success(self, client, mock_conn):
        """Valid token should return a success message"""

        with patch("server.services.users_service.verify_email", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = None  # verify_email returns None on success

            response = await client.post("/auth/verify-email", params={"token": "valid-token"})

            assert response.status_code == 200
            assert response.json() == {"message": "Email verified successfully"}

    
    async def test_verify_email_invalid_token(self, client, mock_conn):
        """Invalid or expired token should return 400"""

        with patch("server.services.users_service.verify_email", new_callable=AsyncMock) as mock_verify:
            mock_verify.side_effect = ValueError("Invalid or expired verification token")

            response = await client.post("/auth/verify-email", params={"token": "bad-token"})

            assert response.status_code == 400
            assert "Invalid or expired" in response.json()["detail"]

    
    async def test_verify_email_server_error(self, client, mock_conn):
        """Unexpected errors should return 500"""

        with patch("server.services.users_service.verify_email", new_callable=AsyncMock) as mock_verify:
            mock_verify.side_effect = Exception("DB exploded")

            response = await client.post("/auth/verify-email", params={"token": "any-token"})

            assert response.status_code == 500


# =================
# POST /auth/login
# =================

class TestLogin:

    
    async def test_login_success_with_email(self, client, mock_conn, make_mock_user):
        """Valid email + password should return access and refresh tokens"""

        mock_user = make_mock_user()

        with patch("server.routers.auth.users_service.get_user_by_email", new_callable=AsyncMock) as mock_get, \
             patch("server.routers.auth.verify_password", return_value=True), \
             patch("server.routers.auth.create_access_token", return_value="fake_access_token"), \
             patch("server.routers.auth.create_refresh_token", return_value="fake_refresh_token"):

            mock_get.return_value = mock_user

            response = await client.post("/auth/login", json={
                "email_or_username": "testuser@mail.uc.edu",
                "password": "correctpassword"
            })

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"

    
    async def test_login_success_with_username(self, client, mock_conn, make_mock_user):
        """Valid username + password should also work"""

        mock_user = make_mock_user()

        with patch("server.routers.auth.users_service.get_user_by_username", new_callable=AsyncMock) as mock_get, \
             patch("server.routers.auth.verify_password", return_value=True), \
             patch("server.routers.auth.create_access_token", return_value="fake_access_token"), \
             patch("server.routers.auth.create_refresh_token", return_value="fake_refresh_token"):

            mock_get.return_value = mock_user

            response = await client.post("/auth/login", json={
                "email_or_username": "testuser",  # No @ so hits get_user_by_username
                "password": "correctpassword"
            })

            assert response.status_code == 200

    
    async def test_login_wrong_password(self, client, mock_conn, make_mock_user):
        """Wrong password should return 401"""

        mock_user = make_mock_user()

        with patch("server.routers.auth.users_service.get_user_by_email", new_callable=AsyncMock) as mock_get, \
             patch("server.routers.auth.verify_password", return_value=False):

            mock_get.return_value = mock_user

            response = await client.post("/auth/login", json={
                "email_or_username": "testuser@mail.uc.edu",
                "password": "wrongpassword"
            })

            assert response.status_code == 401

    
    async def test_login_user_not_found(self, client, mock_conn):
        """Non-existent user should return 401 (same as wrong password — no enumeration!)"""

        with patch("server.routers.auth.users_service.get_user_by_email", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = ValueError("Email not found")

            response = await client.post("/auth/login", json={
                "email_or_username": "ghost@mail.uc.edu",
                "password": "anything"
            })

            assert response.status_code == 401

# ====================
# POST /auth/register
# ====================

class TestRegister:

    
    async def test_register_success(self, client, mock_conn, make_mock_user):
        """Valid registration info should return a UserResponse"""

        mock_user = make_mock_user(email="newuser@mail.uc.edu", is_email_verified=False)

        with patch("server.routers.auth.users_service.register_user", new_callable=AsyncMock) as mock_register, \
             patch("server.routers.auth.emailing_service.send_verification_email", new_callable=AsyncMock):

            mock_register.return_value = mock_user

            response = await client.post("/auth/register", json={
                "email": "newuser@uc.edu",
                "username": "newuser",
                "password": "securepassword"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "newuser@mail.uc.edu"
            assert data["is_email_verified"] == False

    
    async def test_register_duplicate_email(self, client, mock_conn):
        """Duplicate email should return 400"""

        with patch("server.routers.auth.users_service.register_user", new_callable=AsyncMock) as mock_register:
            mock_register.side_effect = ValueError("Email already registered")

            response = await client.post("/auth/register", json={
                "email": "existing@mail.uc.edu",
                "username": "someuser",
                "password": "password123"
            })

            assert response.status_code == 400
            assert "Email already registered" in response.json()["detail"]

# ======================
# POST /auth/reset-password
# ======================

class TestResetPassword:

    
    async def test_reset_password_success(self, client, mock_conn):
        """Valid token and new password should return success message"""

        with patch("server.services.users_service.reset_password", new_callable=AsyncMock) as mock_reset:
            mock_reset.return_value = None

            response = await client.post("/auth/reset-password", params={
                "password_reset_token": "valid-token",
                "new_password": "newSecurePassword123"
            })

            assert response.status_code == 200
            assert response.json() == {"message": "Password reset successfully"}

    
    async def test_reset_password_invalid_token(self, client, mock_conn):
        """Invalid token should return 400"""

        with patch("server.services.users_service.reset_password", new_callable=AsyncMock) as mock_reset:
            mock_reset.side_effect = ValueError("Invalid or expired password reset token")

            response = await client.post("/auth/reset-password", params={
                "password_reset_token": "bad-token",
                "new_password": "newpassword"
            })

            assert response.status_code == 400

# ================
# GET /auth/me
# ================

class TestGetMe:

    
    async def test_get_me_authenticated(self, client, make_mock_user):
        """Authenticated user should get their profile back"""

        mock_user = make_mock_user()

        # Override the get_current_user dependency directly
        from server.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = await client.get("/auth/me")

        assert response.status_code == 200
        assert response.json()["email"] == mock_user.email

    
    async def test_get_me_unauthenticated(self, client):
        """No token should return 401"""

        response = await client.get("/auth/me")
        assert response.status_code == 401