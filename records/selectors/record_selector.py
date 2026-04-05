import logging

from django.db.models import QuerySet

from core.exceptions import NotFoundError
from records.models import FinancialRecord
from users.models import Role, User

logger = logging.getLogger(__name__)


def get_records(*, user: User, filters: dict | None = None) -> QuerySet[FinancialRecord]:
    """Get financial records filtered by role-based scoping."""
    qs = FinancialRecord.objects.select_related("user")

    # Role-based scoping (Layer 3)
    if user.role == Role.MANAGER:
        qs = qs.filter(user=user)
    elif user.role in (Role.ANALYST, Role.ADMIN, Role.AUDITOR):
        pass  # All records
    else:
        return qs.none()

    if not filters:
        return qs

    # Apply filters
    if type_filter := filters.get("type"):
        qs = qs.filter(type=type_filter)

    if category := filters.get("category"):
        qs = qs.filter(category=category)

    if date_from := filters.get("date_from"):
        qs = qs.filter(date__gte=date_from)

    if date_to := filters.get("date_to"):
        qs = qs.filter(date__lte=date_to)

    if min_amount := filters.get("min_amount"):
        qs = qs.filter(amount__gte=min_amount)

    if max_amount := filters.get("max_amount"):
        qs = qs.filter(amount__lte=max_amount)

    if search := filters.get("search"):
        qs = qs.filter(description__icontains=search)

    if tags := filters.get("tags"):
        for tag in tags.split(","):
            qs = qs.filter(tags__icontains=tag.strip())

    # Ordering
    if ordering := filters.get("ordering"):
        allowed_ordering = ("date", "-date", "amount", "-amount", "category", "-category", "created_at", "-created_at")
        if ordering in allowed_ordering:
            qs = qs.order_by(ordering)

    return qs


def get_record_by_id(*, user: User, record_id: int) -> FinancialRecord:
    """Get a single record by ID with role-based access check."""
    try:
        record = FinancialRecord.objects.select_related("user").get(id=record_id)
    except FinancialRecord.DoesNotExist:
        raise NotFoundError("Financial record not found")

    # Role-based access (Layer 4 - object level)
    if user.role == Role.MANAGER and record.user_id != user.id:
        raise NotFoundError("Financial record not found")
    elif user.role == Role.VIEWER:
        raise NotFoundError("Financial record not found")

    return record
