import logging
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from audit.models import AuditAction
from audit.services import audit_service
from core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from records.models import FinancialRecord
from users.models import Role, User

logger = logging.getLogger(__name__)


def create_record(
    *,
    user: User,
    amount: Decimal,
    type: str,
    category: str,
    date: date,
    description: str = "",
    tags: str = "",
) -> FinancialRecord:
    """Create a new financial record."""
    if user.role not in (Role.MANAGER, Role.ADMIN):
        raise PermissionDeniedError("Insufficient role to create records")

    record = FinancialRecord.objects.create(
        user=user,
        amount=amount,
        type=type,
        category=category,
        date=date,
        description=description,
        tags=tags,
    )
    audit_service.log(
        user=user,
        action=AuditAction.CREATE,
        resource_type="FinancialRecord",
        resource_id=record.id,
    )
    logger.info("Record created", extra={"record_id": record.id, "user_id": user.id})
    return record


def update_record(
    *,
    user: User,
    record_id: int,
    data: dict,
) -> FinancialRecord:
    """Update a financial record."""
    if user.role not in (Role.MANAGER, Role.ADMIN):
        raise PermissionDeniedError("Insufficient role to update records")

    try:
        record = FinancialRecord.objects.select_related("user").get(id=record_id)
    except FinancialRecord.DoesNotExist:
        raise NotFoundError("Financial record not found")

    # Managers can only update their own records
    if user.role == Role.MANAGER and record.user_id != user.id:
        raise PermissionDeniedError("You can only modify your own records")

    allowed_fields = ("amount", "type", "category", "date", "description", "tags")
    changes = {}
    update_fields = []
    for field, value in data.items():
        if field in allowed_fields:
            old_value = getattr(record, field)
            setattr(record, field, value)
            update_fields.append(field)
            changes[field] = {"old": str(old_value), "new": str(value)}

    if update_fields:
        record.save(update_fields=update_fields)

    audit_service.log(
        user=user,
        action=AuditAction.UPDATE,
        resource_type="FinancialRecord",
        resource_id=record.id,
        changes=changes,
    )
    logger.info("Record updated", extra={"record_id": record.id, "user_id": user.id})
    return record


def soft_delete_record(*, user: User, record_id: int) -> FinancialRecord:
    """Soft delete a financial record."""
    if user.role not in (Role.MANAGER, Role.ADMIN):
        raise PermissionDeniedError("Insufficient role to delete records")

    try:
        record = FinancialRecord.objects.select_related("user").get(id=record_id)
    except FinancialRecord.DoesNotExist:
        raise NotFoundError("Financial record not found")

    # Managers can only delete their own records
    if user.role == Role.MANAGER and record.user_id != user.id:
        raise PermissionDeniedError("You can only modify your own records")

    record.is_deleted = True
    record.deleted_at = timezone.now()
    record.save(update_fields=["is_deleted", "deleted_at"])

    audit_service.log(
        user=user,
        action=AuditAction.DELETE,
        resource_type="FinancialRecord",
        resource_id=record.id,
    )
    logger.info("Record soft deleted", extra={"record_id": record.id, "user_id": user.id})
    return record


def bulk_create_records(
    *,
    user: User,
    records_data: list[dict],
) -> list[FinancialRecord]:
    """Bulk create financial records (admin only)."""
    if user.role != Role.ADMIN:
        raise PermissionDeniedError("Only admins can bulk create records")

    if len(records_data) > 100:
        raise ValidationError("Maximum 100 records per batch")

    records = []
    with transaction.atomic():
        for data in records_data:
            record = FinancialRecord(
                user=user,
                amount=data["amount"],
                type=data["type"],
                category=data["category"],
                date=data["date"],
                description=data.get("description", ""),
                tags=data.get("tags", ""),
            )
            records.append(record)

        created = FinancialRecord.objects.bulk_create(records)

    audit_service.log(
        user=user,
        action=AuditAction.CREATE,
        resource_type="FinancialRecord",
        changes={"bulk_count": len(created)},
    )
    logger.info("Bulk created %d records", len(created), extra={"user_id": user.id})
    return created
