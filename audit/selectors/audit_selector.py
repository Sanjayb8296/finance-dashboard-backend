from django.db.models import QuerySet

from audit.models import AuditLog
from core.exceptions import NotFoundError


def get_audit_logs(*, filters: dict | None = None) -> QuerySet[AuditLog]:
    """Get audit logs with optional filtering."""
    qs = AuditLog.objects.select_related("user")

    if not filters:
        return qs

    if action := filters.get("action"):
        qs = qs.filter(action=action)

    if resource_type := filters.get("resource_type"):
        qs = qs.filter(resource_type=resource_type)

    if user_id := filters.get("user_id"):
        qs = qs.filter(user_id=user_id)

    if date_from := filters.get("date_from"):
        qs = qs.filter(timestamp__date__gte=date_from)

    if date_to := filters.get("date_to"):
        qs = qs.filter(timestamp__date__lte=date_to)

    return qs


def get_audit_log_by_id(*, log_id: int) -> AuditLog:
    """Get a single audit log by ID."""
    try:
        return AuditLog.objects.select_related("user").get(id=log_id)
    except AuditLog.DoesNotExist:
        raise NotFoundError("Audit log not found")
