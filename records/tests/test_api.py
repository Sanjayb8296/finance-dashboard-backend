from datetime import date
from decimal import Decimal

import pytest
from rest_framework import status

from records.models import Category, FinancialRecord, RecordType


@pytest.fixture
def sample_record(manager_user):
    return FinancialRecord.objects.create(
        user=manager_user,
        amount=Decimal("1000.00"),
        type=RecordType.INCOME,
        category=Category.SALARY,
        date=date.today(),
        description="Test salary",
    )


@pytest.fixture
def record_data():
    return {
        "amount": "5000.00",
        "type": "income",
        "category": "salary",
        "date": str(date.today()),
        "description": "Monthly salary",
    }


@pytest.mark.django_db
class TestRecordPermissions:
    """Permission tests for financial record endpoints - highest impact."""

    # Create permissions
    def test_manager_can_create_record(self, manager_client, record_data):
        response = manager_client.post("/api/v1/records/", record_data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_admin_can_create_record(self, admin_client, record_data):
        response = admin_client.post("/api/v1/records/", record_data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_viewer_cannot_create_record(self, viewer_client, record_data):
        response = viewer_client.post("/api/v1/records/", record_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_cannot_create_record(self, analyst_client, record_data):
        response = analyst_client.post("/api/v1/records/", record_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auditor_cannot_create_record(self, auditor_client, record_data):
        response = auditor_client.post("/api/v1/records/", record_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # List permissions
    def test_analyst_can_list_records(self, analyst_client):
        response = analyst_client.get("/api/v1/records/")
        assert response.status_code == status.HTTP_200_OK

    def test_manager_can_list_records(self, manager_client):
        response = manager_client.get("/api/v1/records/")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_list_records(self, admin_client):
        response = admin_client.get("/api/v1/records/")
        assert response.status_code == status.HTTP_200_OK

    def test_auditor_can_list_records(self, auditor_client):
        response = auditor_client.get("/api/v1/records/")
        assert response.status_code == status.HTTP_200_OK

    def test_viewer_cannot_list_records(self, viewer_client):
        response = viewer_client.get("/api/v1/records/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # Manager scope - can only see own records
    def test_manager_only_sees_own_records(self, manager_client, manager_user, admin_user):
        FinancialRecord.objects.create(
            user=manager_user, amount=Decimal("100"), type="income",
            category="salary", date=date.today(),
        )
        FinancialRecord.objects.create(
            user=admin_user, amount=Decimal("200"), type="income",
            category="salary", date=date.today(),
        )
        response = manager_client.get("/api/v1/records/")
        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["user"]["id"] == manager_user.id

    # Update permissions
    def test_manager_can_update_own_record(self, manager_client, sample_record):
        response = manager_client.patch(
            f"/api/v1/records/{sample_record.id}/",
            {"amount": "2000.00"},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_manager_cannot_update_others_record(self, manager_client, admin_user):
        other_record = FinancialRecord.objects.create(
            user=admin_user, amount=Decimal("100"), type="income",
            category="salary", date=date.today(),
        )
        response = manager_client.patch(
            f"/api/v1/records/{other_record.id}/",
            {"amount": "2000.00"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_update_any_record(self, admin_client, sample_record):
        response = admin_client.patch(
            f"/api/v1/records/{sample_record.id}/",
            {"amount": "2000.00"},
        )
        assert response.status_code == status.HTTP_200_OK

    # Delete permissions
    def test_manager_can_soft_delete_own_record(self, manager_client, sample_record):
        response = manager_client.delete(f"/api/v1/records/{sample_record.id}/")
        assert response.status_code == status.HTTP_200_OK
        sample_record.refresh_from_db()
        assert sample_record.is_deleted is True

    def test_soft_deleted_record_not_in_list(self, manager_client, sample_record):
        sample_record.soft_delete()
        response = manager_client.get("/api/v1/records/")
        assert len(response.data["results"]) == 0


@pytest.mark.django_db
class TestRecordFiltering:
    def test_filter_by_type(self, manager_client, manager_user):
        FinancialRecord.objects.create(
            user=manager_user, amount=Decimal("100"), type="income",
            category="salary", date=date.today(),
        )
        FinancialRecord.objects.create(
            user=manager_user, amount=Decimal("50"), type="expense",
            category="rent", date=date.today(),
        )
        response = manager_client.get("/api/v1/records/?type=income")
        assert len(response.data["results"]) == 1

    def test_search_by_description(self, manager_client, manager_user):
        FinancialRecord.objects.create(
            user=manager_user, amount=Decimal("100"), type="income",
            category="salary", date=date.today(), description="Monthly salary",
        )
        FinancialRecord.objects.create(
            user=manager_user, amount=Decimal("50"), type="expense",
            category="rent", date=date.today(), description="Office rent",
        )
        response = manager_client.get("/api/v1/records/?search=salary")
        assert len(response.data["results"]) == 1


@pytest.mark.django_db
class TestRecordExport:
    def test_analyst_can_export_csv(self, analyst_client, manager_user):
        FinancialRecord.objects.create(
            user=manager_user, amount=Decimal("100"), type="income",
            category="salary", date=date.today(),
        )
        response = analyst_client.get("/api/v1/records/export/")
        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "text/csv"

    def test_viewer_cannot_export_csv(self, viewer_client):
        response = viewer_client.get("/api/v1/records/export/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
