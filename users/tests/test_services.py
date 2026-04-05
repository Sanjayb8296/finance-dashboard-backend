import pytest

from core.exceptions import ConflictError, PermissionDeniedError, ValidationError
from users.models import Role, User
from users.services import user_service


@pytest.mark.django_db
class TestUserService:
    def test_register_user_creates_viewer(self):
        user = user_service.register_user(
            email="test@example.com",
            name="Test User",
            password="testpass123!",
        )
        assert user.role == Role.VIEWER
        assert user.email == "test@example.com"

    def test_register_duplicate_email_raises_conflict(self, viewer_user):
        with pytest.raises(ConflictError):
            user_service.register_user(
                email=viewer_user.email,
                name="Duplicate",
                password="testpass123!",
            )

    def test_authenticate_user_success(self, viewer_user):
        user = user_service.authenticate_user(
            email=viewer_user.email,
            password="testpass123!",
        )
        assert user.id == viewer_user.id

    def test_authenticate_invalid_password_raises(self, viewer_user):
        with pytest.raises(ValidationError):
            user_service.authenticate_user(
                email=viewer_user.email,
                password="wrong",
            )

    def test_create_user_as_admin(self, admin_user):
        user = user_service.create_user(
            admin=admin_user,
            email="new@test.com",
            name="New User",
            password="testpass123!",
            role=Role.ANALYST,
        )
        assert user.role == Role.ANALYST

    def test_create_user_as_non_admin_raises(self, manager_user):
        with pytest.raises(PermissionDeniedError):
            user_service.create_user(
                admin=manager_user,
                email="new@test.com",
                name="New User",
                password="testpass123!",
            )

    def test_update_user_as_admin(self, admin_user, viewer_user):
        user = user_service.update_user(
            admin=admin_user,
            user_id=viewer_user.id,
            data={"role": Role.ANALYST},
        )
        assert user.role == Role.ANALYST

    def test_admin_cannot_demote_self(self, admin_user):
        with pytest.raises(ValidationError):
            user_service.update_user(
                admin=admin_user,
                user_id=admin_user.id,
                data={"role": Role.VIEWER},
            )

    def test_deactivate_last_admin_raises(self, admin_user):
        with pytest.raises(ValidationError):
            user_service.deactivate_user(
                admin=admin_user,
                user_id=admin_user.id,
            )

    def test_update_profile(self, viewer_user):
        user = user_service.update_profile(
            user=viewer_user,
            data={"name": "Updated Name"},
        )
        assert user.name == "Updated Name"
