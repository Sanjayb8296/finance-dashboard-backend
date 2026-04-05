from datetime import date
from decimal import Decimal

import pytest
from rest_framework import status

from records.models import FinancialRecord


@pytest.mark.django_db
class TestRecordEdgeCases:
    def test_zero_amount_rejected(self, manager_client):
        response = manager_client.post("/api/v1/records/", {
            "amount": "0.00",
            "type": "income",
            "category": "salary",
            "date": str(date.today()),
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_negative_amount_rejected(self, manager_client):
        response = manager_client.post("/api/v1/records/", {
            "amount": "-100.00",
            "type": "income",
            "category": "salary",
            "date": str(date.today()),
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_category_rejected(self, manager_client):
        response = manager_client.post("/api/v1/records/", {
            "amount": "100.00",
            "type": "income",
            "category": "invalid_category",
            "date": str(date.today()),
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_type_rejected(self, manager_client):
        response = manager_client.post("/api/v1/records/", {
            "amount": "100.00",
            "type": "transfer",
            "category": "salary",
            "date": str(date.today()),
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_empty_description_allowed(self, manager_client):
        response = manager_client.post("/api/v1/records/", {
            "amount": "100.00",
            "type": "income",
            "category": "salary",
            "date": str(date.today()),
            "description": "",
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_future_date_allowed(self, manager_client):
        response = manager_client.post("/api/v1/records/", {
            "amount": "100.00",
            "type": "income",
            "category": "salary",
            "date": "2027-12-31",
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_deleted_record_returns_404(self, manager_client, manager_user):
        record = FinancialRecord.objects.create(
            user=manager_user, amount=Decimal("100"), type="income",
            category="salary", date=date.today(),
        )
        record.soft_delete()
        response = manager_client.get(f"/api/v1/records/{record.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_nonexistent_record_returns_404(self, manager_client):
        response = manager_client.get("/api/v1/records/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_request_returns_401(self, api_client):
        response = api_client.get("/api/v1/records/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestBulkCreate:
    def test_admin_can_bulk_create(self, admin_client):
        response = admin_client.post(
            "/api/v1/records/bulk/",
            {
                "records": [
                    {"amount": "1000", "type": "income", "category": "freelance", "date": "2026-03-01"},
                    {"amount": "500", "type": "expense", "category": "rent", "date": "2026-03-02"},
                ]
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["data"]) == 2

    def test_manager_cannot_bulk_create(self, manager_client):
        response = manager_client.post(
            "/api/v1/records/bulk/",
            {
                "records": [
                    {"amount": "1000", "type": "income", "category": "freelance", "date": "2026-03-01"},
                ]
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_bulk_create_empty_list_rejected(self, admin_client):
        response = admin_client.post(
            "/api/v1/records/bulk/",
            {"records": []},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestHealthCheck:
    def test_health_check_no_auth(self, api_client):
        response = api_client.get("/api/v1/health/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["status"] == "healthy"
        assert response.data["data"]["database"] == "connected"


@pytest.mark.django_db
class TestResponseFormat:
    """Ensure all responses follow the consistent envelope format."""

    def test_success_response_format(self, manager_client):
        response = manager_client.post("/api/v1/records/", {
            "amount": "100.00",
            "type": "income",
            "category": "salary",
            "date": str(date.today()),
        })
        assert "success" in response.data
        assert "message" in response.data
        assert "data" in response.data
        assert "errors" in response.data
        assert response.data["success"] is True

    def test_error_response_format(self, viewer_client):
        response = viewer_client.post("/api/v1/records/", {
            "amount": "100.00",
            "type": "income",
            "category": "salary",
            "date": str(date.today()),
        })
        assert "success" in response.data
        assert response.data["success"] is False
