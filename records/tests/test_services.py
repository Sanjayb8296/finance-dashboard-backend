from datetime import date
from decimal import Decimal

import pytest

from core.exceptions import NotFoundError, PermissionDeniedError
from records.models import Category, FinancialRecord, RecordType
from records.services import record_service


@pytest.fixture
def manager_record(manager_user):
    return FinancialRecord.objects.create(
        user=manager_user,
        amount=Decimal("1000.00"),
        type=RecordType.INCOME,
        category=Category.SALARY,
        date=date.today(),
    )


@pytest.mark.django_db
class TestRecordService:
    def test_create_record_as_manager(self, manager_user):
        record = record_service.create_record(
            user=manager_user,
            amount=Decimal("5000.00"),
            type="income",
            category="salary",
            date=date.today(),
        )
        assert record.amount == Decimal("5000.00")
        assert record.user == manager_user

    def test_create_record_as_viewer_raises(self, viewer_user):
        with pytest.raises(PermissionDeniedError):
            record_service.create_record(
                user=viewer_user,
                amount=Decimal("100.00"),
                type="income",
                category="salary",
                date=date.today(),
            )

    def test_update_record_as_owner(self, manager_user, manager_record):
        record = record_service.update_record(
            user=manager_user,
            record_id=manager_record.id,
            data={"amount": Decimal("2000.00")},
        )
        assert record.amount == Decimal("2000.00")

    def test_update_others_record_as_manager_raises(self, manager_user, admin_user):
        other_record = FinancialRecord.objects.create(
            user=admin_user, amount=Decimal("100"), type="income",
            category="salary", date=date.today(),
        )
        with pytest.raises(PermissionDeniedError):
            record_service.update_record(
                user=manager_user,
                record_id=other_record.id,
                data={"amount": Decimal("999")},
            )

    def test_soft_delete_record(self, manager_user, manager_record):
        record = record_service.soft_delete_record(
            user=manager_user,
            record_id=manager_record.id,
        )
        assert record.is_deleted is True
        assert record.deleted_at is not None

    def test_update_nonexistent_record_raises(self, admin_user):
        with pytest.raises(NotFoundError):
            record_service.update_record(
                user=admin_user,
                record_id=99999,
                data={"amount": Decimal("100")},
            )
