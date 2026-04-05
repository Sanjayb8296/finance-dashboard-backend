import pytest
from rest_framework import status

from users.models import Role, User


@pytest.mark.django_db
class TestAuthEndpoints:
    def test_register_creates_user_with_viewer_role(self, api_client):
        response = api_client.post("/api/v1/auth/register/", {
            "email": "new@test.com",
            "name": "New User",
            "password": "testpass123!",
            "password_confirm": "testpass123!",
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["role"] == Role.VIEWER

    def test_register_duplicate_email_returns_conflict(self, api_client, viewer_user):
        response = api_client.post("/api/v1/auth/register/", {
            "email": viewer_user.email,
            "name": "Duplicate",
            "password": "testpass123!",
            "password_confirm": "testpass123!",
        })
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_register_password_mismatch_returns_400(self, api_client):
        response = api_client.post("/api/v1/auth/register/", {
            "email": "new@test.com",
            "name": "New User",
            "password": "testpass123!",
            "password_confirm": "different!",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_returns_tokens(self, api_client, viewer_user):
        response = api_client.post("/api/v1/auth/login/", {
            "email": viewer_user.email,
            "password": "testpass123!",
        })
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data["data"]
        assert "refresh" in response.data["data"]

    def test_login_invalid_credentials_returns_400(self, api_client, viewer_user):
        response = api_client.post("/api/v1/auth/login/", {
            "email": viewer_user.email,
            "password": "wrong",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_blacklists_token(self, api_client, viewer_user):
        login_response = api_client.post("/api/v1/auth/login/", {
            "email": viewer_user.email,
            "password": "testpass123!",
        })
        refresh = login_response.data["data"]["refresh"]
        access = login_response.data["data"]["access"]

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post("/api/v1/auth/logout/", {"refresh": refresh})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProfileEndpoints:
    def test_get_profile_authenticated(self, manager_client, manager_user):
        response = manager_client.get("/api/v1/users/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["email"] == manager_user.email

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get("/api/v1/users/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_name(self, viewer_client):
        response = viewer_client.patch("/api/v1/users/me/", {"name": "Updated Name"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["name"] == "Updated Name"


@pytest.mark.django_db
class TestUserPermissions:
    """Test that role-based access control works correctly for user management."""

    def test_admin_can_list_users(self, admin_client):
        response = admin_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_200_OK

    def test_auditor_can_list_users(self, auditor_client):
        response = auditor_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_200_OK

    def test_viewer_cannot_list_users(self, viewer_client):
        response = viewer_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_manager_cannot_list_users(self, manager_client):
        response = manager_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_cannot_list_users(self, analyst_client):
        response = analyst_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_create_user(self, admin_client):
        response = admin_client.post("/api/v1/users/", {
            "email": "created@test.com",
            "name": "Created User",
            "password": "testpass123!",
            "role": "analyst",
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_auditor_cannot_create_user(self, auditor_client):
        response = auditor_client.post("/api/v1/users/", {
            "email": "created@test.com",
            "name": "Created User",
            "password": "testpass123!",
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_deactivate_user(self, admin_client, viewer_user):
        response = admin_client.delete(f"/api/v1/users/{viewer_user.id}/")
        assert response.status_code == status.HTTP_200_OK
        viewer_user.refresh_from_db()
        assert viewer_user.is_active is False

    def test_admin_cannot_deactivate_self(self, admin_client, admin_user):
        response = admin_client.delete(f"/api/v1/users/{admin_user.id}/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_cannot_deactivate_last_admin(self, admin_client, admin_user):
        response = admin_client.delete(f"/api/v1/users/{admin_user.id}/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_cannot_demote_self(self, admin_client, admin_user):
        response = admin_client.patch(f"/api/v1/users/{admin_user.id}/", {"role": "viewer"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
