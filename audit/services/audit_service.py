import logging

from audit.models import AuditAction, AuditLog
from users.models import User

logger = logging.getLogger(__name__)


def log(
    *,
    user: User | None,
    action: str,
    resource_type: str,
    resource_id: int | None = None,
    changes: dict | None = None,
    ip_address: str | None = None,
    user_agent: str = "",
) -> AuditLog:
    """Create an audit log entry."""
    entry = AuditLog.objects.create(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        changes=changes or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    logger.info(
        "Audit: %s %s %s:%s",
        user.email if user else "anonymous",
        action,
        resource_type,
        resource_id,
    )
    return entry


def get_client_ip(request) -> str | None:
    """Extract client IP from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
