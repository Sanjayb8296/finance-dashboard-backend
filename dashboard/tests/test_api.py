from datetime import date
from decimal import Decimal

import pytest
from rest_framework import status

from records.models import Category, FinancialRecord, RecordType


@pytest.fixture
def records_fixture(manager_user, admin_user):
    """Create a set of records for dashboard tests."""
    records = [
        FinancialRecord(user=manager_user, amount=Decimal("5000"), type=RecordType.INCOME, category=Category.SALARY, date=date(2026, 3, 1)),
        FinancialRecord(user=manager_user, amount=Decimal("2000"), type=RecordType.INCOME, category=Category.FREELANCE, date=date(2026, 3, 15)),
        FinancialRecord(user=manager_user, amount=Decimal("1200"), type=RecordType.EXPENSE, category=Category.RENT, date=date(2026, 3, 1)),
        FinancialRecord(user=manager_user, amount=Decimal("300"), type=RecordType.EXPENSE, category=Category.GROCERIES, date=date(2026, 3, 10)),
        FinancialRecord(user=admin_user, amount=Decimal("8000"), type=RecordType.INCOME, category=Category.SALARY, date=date(2026, 2, 1)),
        FinancialRecord(user=admin_user, amount=Decimal("500"), type=RecordType.EXPENSE, category=Category.UTILITIES, date=date(2026, 2, 15)),
    ]
    FinancialRecord.objects.bulk_create(records)
    return records


@pytest.mark.django_db
class TestDashboardSummary:
    def test_viewer_can_access_summary(self, viewer_client, records_fixture):
        response = viewer_client.get("/api/v1/dashboard/summary/")
        assert response.status_code == status.HTTP_200_OK
        data = response.data["data"]
        assert Decimal(str(data["total_income"])) == Decimal("0.00")
        assert Decimal(str(data["total_expense"])) == Decimal("0.00")
        assert data["record_count"] == 0

    def test_summary_returns_correct_totals(self, admin_client, records_fixture):
        response = admin_client.get("/api/v1/dashboard/summary/")
        data = response.data["data"]
        assert Decimal(str(data["total_income"])) == Decimal("15000.00")
        assert Decimal(str(data["total_expense"])) == Decimal("2000.00")
        assert Decimal(str(data["net_balance"])) == Decimal("13000.00")
        assert data["record_count"] == 6

    def test_manager_summary_only_includes_own(self, manager_client, records_fixture):
        response = manager_client.get("/api/v1/dashboard/summary/")
        data = response.data["data"]
        # Manager should only see their own records
        assert Decimal(str(data["total_income"])) == Decimal("7000.00")
        assert Decimal(str(data["total_expense"])) == Decimal("1500.00")
        assert data["record_count"] == 4

    def test_summary_with_date_filter(self, admin_client, records_fixture):
        response = admin_client.get("/api/v1/dashboard/summary/?date_from=2026-03-01&date_to=2026-03-31")
        data = response.data["data"]
        assert Decimal(str(data["total_income"])) == Decimal("7000.00")

    def test_summary_empty_dataset_returns_zeros(self, viewer_client):
        response = viewer_client.get("/api/v1/dashboard/summary/")
        assert response.status_code == status.HTTP_200_OK
        data = response.data["data"]
        assert Decimal(str(data["total_income"])) == Decimal("0.00")
        assert data["record_count"] == 0

    def test_unauthenticated_cannot_access_summary(self, api_client):
        response = api_client.get("/api/v1/dashboard/summary/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDashboardTrends:
    def test_trends_returns_monthly_data(self, admin_client, records_fixture):
        response = admin_client.get("/api/v1/dashboard/trends/")
        assert response.status_code == status.HTTP_200_OK
        trends = response.data["data"]["trends"]
        assert len(trends) > 0
        assert "month" in trends[0]
        assert "income" in trends[0]
        assert "expense" in trends[0]

    def test_viewer_trends_only_include_own_data(self, viewer_client, records_fixture):
        response = viewer_client.get("/api/v1/dashboard/trends/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["trends"] == []


@pytest.mark.django_db
class TestDashboardCategoryBreakdown:
    def test_category_breakdown(self, admin_client, records_fixture):
        response = admin_client.get("/api/v1/dashboard/category-breakdown/?type=expense")
        assert response.status_code == status.HTTP_200_OK
        data = response.data["data"]
        assert "breakdown" in data
        assert "grand_total" in data

    def test_viewer_category_breakdown_only_includes_own_data(self, viewer_client, records_fixture):
        response = viewer_client.get("/api/v1/dashboard/category-breakdown/?type=expense")
        assert response.status_code == status.HTTP_200_OK
        data = response.data["data"]
        assert data["breakdown"] == []
        assert Decimal(str(data["grand_total"])) == Decimal("0.00")


@pytest.mark.django_db
class TestDashboardRecent:
    def test_recent_transactions(self, admin_client, records_fixture):
        response = admin_client.get("/api/v1/dashboard/recent/?limit=3")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) <= 3

    def test_viewer_recent_transactions_only_include_own_data(self, viewer_client, records_fixture):
        response = viewer_client.get("/api/v1/dashboard/recent/?limit=3")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"] == []
