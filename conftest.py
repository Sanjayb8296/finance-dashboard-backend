import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Role, User


@pytest.fixture
def api_client():
    return APIClient()


def _create_user(role, email=None):
    if email is None:
        email = f"{role}@test.com"
    user = User.objects.create_user(
        email=email,
        name=f"Test {role.title()}",
        password="testpass123!",
        role=role,
    )
    return user


def _auth_client(user):
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


@pytest.fixture
def admin_user(db):
    return _create_user(Role.ADMIN, "admin@test.com")


@pytest.fixture
def manager_user(db):
    return _create_user(Role.MANAGER, "manager@test.com")


@pytest.fixture
def analyst_user(db):
    return _create_user(Role.ANALYST, "analyst@test.com")


@pytest.fixture
def viewer_user(db):
    return _create_user(Role.VIEWER, "viewer@test.com")


@pytest.fixture
def auditor_user(db):
    return _create_user(Role.AUDITOR, "auditor@test.com")


@pytest.fixture
def admin_client(admin_user):
    return _auth_client(admin_user)


@pytest.fixture
def manager_client(manager_user):
    return _auth_client(manager_user)


@pytest.fixture
def analyst_client(analyst_user):
    return _auth_client(analyst_user)


@pytest.fixture
def viewer_client(viewer_user):
    return _auth_client(viewer_user)


@pytest.fixture
def auditor_client(auditor_user):
    return _auth_client(auditor_user)
