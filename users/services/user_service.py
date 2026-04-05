import logging
from typing import Any

from django.contrib.auth import authenticate

from core.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from users.models import Role, User

logger = logging.getLogger(__name__)


def register_user(*, email: str, name: str, password: str) -> User:
    """Register a new user with default VIEWER role."""
    if User.objects.filter(email=email).exists():
        raise ConflictError("User with this email already exists")

    user = User.objects.create_user(email=email, name=name, password=password)
    logger.info("User registered", extra={"user_id": user.id, "email": user.email})
    return user


def authenticate_user(*, email: str, password: str) -> User:
    """Authenticate user and return user object."""
    user = authenticate(email=email, password=password)
    if user is None:
        raise ValidationError("Invalid email or password")
    if not user.is_active:
        raise PermissionDeniedError("Account is deactivated")
    return user


def create_user(*, admin: User, email: str, name: str, password: str, role: str = Role.VIEWER) -> User:
    """Create a new user (admin only)."""
    if admin.role != Role.ADMIN:
        raise PermissionDeniedError("Only admins can create users")

    if User.objects.filter(email=email).exists():
        raise ConflictError("User with this email already exists")

    user = User.objects.create_user(email=email, name=name, password=password, role=role)
    logger.info("User created by admin", extra={"user_id": user.id, "admin_id": admin.id})
    return user


def update_user(*, admin: User, user_id: int, data: dict[str, Any]) -> User:
    """Update a user (admin only)."""
    if admin.role != Role.ADMIN:
        raise PermissionDeniedError("Only admins can update users")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFoundError("User not found")

    # Prevent admin from demoting themselves
    if user.id == admin.id and "role" in data and data["role"] != Role.ADMIN:
        raise ValidationError("Cannot demote yourself")

    for field, value in data.items():
        if field in ("name", "role", "is_active"):
            setattr(user, field, value)

    user.save(update_fields=[f for f in data if f in ("name", "role", "is_active")])
    logger.info("User updated", extra={"user_id": user.id, "admin_id": admin.id})
    return user


def deactivate_user(*, admin: User, user_id: int) -> User:
    """Deactivate a user (admin only)."""
    if admin.role != Role.ADMIN:
        raise PermissionDeniedError("Only admins can deactivate users")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFoundError("User not found")

    if user.id == admin.id:
        raise ValidationError("Cannot deactivate yourself")

    # Prevent deactivating the last admin
    if user.role == Role.ADMIN:
        admin_count = User.objects.filter(role=Role.ADMIN, is_active=True).count()
        if admin_count <= 1:
            raise ValidationError("Cannot deactivate the last admin")

    user.is_active = False
    user.save(update_fields=["is_active"])
    logger.info("User deactivated", extra={"user_id": user.id, "admin_id": admin.id})
    return user


def update_profile(*, user: User, data: dict[str, Any]) -> User:
    """Update own profile (name only)."""
    if "name" in data:
        user.name = data["name"]
        user.save(update_fields=["name"])
    return user
