from datetime import date
from decimal import Decimal

import pytest
from rest_framework import status

from audit.models import AuditAction, AuditLog
from audit.services import audit_service
from records.models import FinancialRecord


@pytest.fixture
def sample_audit_logs(admin_user, manager_user):
    """Create sample audit log entries."""
    audit_service.log(
        user=admin_user,
        action=AuditAction.CREATE,
        resource_type="FinancialRecord",
        resource_id=1,
    )
    audit_service.log(
        user=manager_user,
        action=AuditAction.UPDATE,
        resource_type="FinancialRecord",
        resource_id=1,
        changes={"amount": {"old": "100.00", "new": "200.00"}},
    )
    audit_service.log(
        user=admin_user,
        action=AuditAction.DELETE,
        resource_type="FinancialRecord",
        resource_id=2,
    )


@pytest.mark.django_db
class TestAuditLogPermissions:
    def test_admin_can_list_audit_logs(self, admin_client, sample_audit_logs):
        response = admin_client.get("/api/v1/audit/logs/")
        assert response.status_code == status.HTTP_200_OK

    def test_auditor_can_list_audit_logs(self, auditor_client, sample_audit_logs):
        response = auditor_client.get("/api/v1/audit/logs/")
        assert response.status_code == status.HTTP_200_OK

    def test_viewer_cannot_list_audit_logs(self, viewer_client):
        response = viewer_client.get("/api/v1/audit/logs/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_manager_cannot_list_audit_logs(self, manager_client):
        response = manager_client.get("/api/v1/audit/logs/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_cannot_list_audit_logs(self, analyst_client):
        response = analyst_client.get("/api/v1/audit/logs/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAuditLogDetail:
    def test_admin_can_view_detail(self, admin_client, sample_audit_logs):
        log = AuditLog.objects.first()
        response = admin_client.get(f"/api/v1/audit/logs/{log.id}/")
        assert response.status_code == status.HTTP_200_OK

    def test_nonexistent_log_returns_404(self, admin_client):
        response = admin_client.get("/api/v1/audit/logs/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestAuditTrailIntegration:
    """Test that CRUD operations create audit log entries."""

    def test_creating_record_creates_audit_log(self, manager_client):
        manager_client.post("/api/v1/records/", {
            "amount": "1000.00",
            "type": "income",
            "category": "salary",
            "date": str(date.today()),
        })
        assert AuditLog.objects.filter(action=AuditAction.CREATE, resource_type="FinancialRecord").exists()

    def test_updating_record_creates_audit_log(self, manager_client, manager_user):
        record = FinancialRecord.objects.create(
            user=manager_user, amount=Decimal("100"), type="income",
            category="salary", date=date.today(),
        )
        manager_client.patch(f"/api/v1/records/{record.id}/", {"amount": "200.00"})
        assert AuditLog.objects.filter(action=AuditAction.UPDATE, resource_type="FinancialRecord").exists()

    def test_deleting_record_creates_audit_log(self, manager_client, manager_user):
        record = FinancialRecord.objects.create(
            user=manager_user, amount=Decimal("100"), type="income",
            category="salary", date=date.today(),
        )
        manager_client.delete(f"/api/v1/records/{record.id}/")
        assert AuditLog.objects.filter(action=AuditAction.DELETE, resource_type="FinancialRecord").exists()
