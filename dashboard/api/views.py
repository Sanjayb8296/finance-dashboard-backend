from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.api.serializers import (
    CategoryBreakdownItemSerializer,
    DashboardSummarySerializer,
    TrendItemSerializer,
)
from dashboard.selectors import dashboard_selector
from records.api.serializers import RecordOutputSerializer


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="date_from", type=str, description="Start date (YYYY-MM-DD)"),
            OpenApiParameter(name="date_to", type=str, description="End date (YYYY-MM-DD)"),
        ],
        responses={200: DashboardSummarySerializer},
        summary="Financial summary",
        description="Get financial summary with totals, averages, and extremes. All roles.",
        tags=["Dashboard"],
    )
    def get(self, request):
        summary = dashboard_selector.get_summary(
            user=request.user,
            date_from=request.query_params.get("date_from"),
            date_to=request.query_params.get("date_to"),
        )

        return Response(
            {
                "success": True,
                "message": "Dashboard summary retrieved",
                "data": summary,
                "errors": None,
            },
        )


class DashboardTrendsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="months", type=int, description="Number of months (default 12)"),
        ],
        responses={200: TrendItemSerializer(many=True)},
        summary="Monthly income/expense trends",
        description="Get monthly trends. All roles.",
        tags=["Dashboard"],
    )
    def get(self, request):
        months = int(request.query_params.get("months", 12))
        trends = dashboard_selector.get_trends(
            user=request.user,
            months=months,
        )

        return Response(
            {
                "success": True,
                "message": "Trends retrieved",
                "data": {"trends": trends},
                "errors": None,
            },
        )


class DashboardCategoryBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="type", enum=["income", "expense"], description="Filter by record type"),
            OpenApiParameter(name="date_from", type=str, description="Start date (YYYY-MM-DD)"),
            OpenApiParameter(name="date_to", type=str, description="End date (YYYY-MM-DD)"),
        ],
        responses={200: CategoryBreakdownItemSerializer(many=True)},
        summary="Category-wise breakdown",
        description="Get category-wise totals with percentages. All roles.",
        tags=["Dashboard"],
    )
    def get(self, request):
        data = dashboard_selector.get_category_breakdown(
            user=request.user,
            type_filter=request.query_params.get("type"),
            date_from=request.query_params.get("date_from"),
            date_to=request.query_params.get("date_to"),
        )

        return Response(
            {
                "success": True,
                "message": "Category breakdown retrieved",
                "data": data,
                "errors": None,
            },
        )


class DashboardRecentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="limit", type=int, description="Number of records (default 10)"),
        ],
        responses={200: RecordOutputSerializer(many=True)},
        summary="Recent transactions",
        description="Get recent transactions. All roles.",
        tags=["Dashboard"],
    )
    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        records = dashboard_selector.get_recent_transactions(
            user=request.user,
            limit=limit,
        )

        return Response(
            {
                "success": True,
                "message": "Recent transactions retrieved",
                "data": RecordOutputSerializer(records, many=True).data,
                "errors": None,
            },
        )
