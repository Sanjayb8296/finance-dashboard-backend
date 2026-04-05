from django.urls import path

from dashboard.api.views import (
    DashboardCategoryBreakdownView,
    DashboardRecentView,
    DashboardSummaryView,
    DashboardTrendsView,
)

urlpatterns = [
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("dashboard/trends/", DashboardTrendsView.as_view(), name="dashboard-trends"),
    path("dashboard/category-breakdown/", DashboardCategoryBreakdownView.as_view(), name="dashboard-category-breakdown"),
    path("dashboard/recent/", DashboardRecentView.as_view(), name="dashboard-recent"),
]
