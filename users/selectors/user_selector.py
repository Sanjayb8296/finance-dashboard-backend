from django.db.models import QuerySet

from users.models import User


def get_users(*, filters: dict | None = None) -> QuerySet[User]:
    """Get all users with optional filtering."""
    qs = User.objects.all().order_by("-created_at")

    if not filters:
        return qs

    if role := filters.get("role"):
        qs = qs.filter(role=role)

    if is_active := filters.get("is_active"):
        qs = qs.filter(is_active=is_active.lower() == "true")

    if search := filters.get("search"):
        qs = qs.filter(email__icontains=search) | qs.filter(name__icontains=search)

    return qs


def get_user_by_id(*, user_id: int) -> User | None:
    """Get a single user by ID."""
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
