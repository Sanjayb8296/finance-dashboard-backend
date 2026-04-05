from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.api.serializers import AuditLogOutputSerializer
from audit.selectors import audit_selector
from core.pagination import StandardPagination
from users.permissions.user_permissions import IsAdminOrAuditor


class AuditLogListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrAuditor]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="action", description="Filter by action type"),
            OpenApiParameter(name="resource_type", description="Filter by resource type"),
            OpenApiParameter(name="user_id", type=int, description="Filter by user ID"),
            OpenApiParameter(name="date_from", type=str, description="Start date (YYYY-MM-DD)"),
            OpenApiParameter(name="date_to", type=str, description="End date (YYYY-MM-DD)"),
            OpenApiParameter(name="page", type=int, description="Page number"),
        ],
        responses={200: AuditLogOutputSerializer(many=True)},
        summary="List audit logs",
        description="List audit logs. ADMIN and AUDITOR only.",
        tags=["Audit"],
    )
    def get(self, request):
        logs = audit_selector.get_audit_logs(filters=request.query_params)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(logs, request)

        return paginator.get_paginated_response(
            AuditLogOutputSerializer(page, many=True).data,
        )


class AuditLogDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrAuditor]

    @extend_schema(
        responses={200: AuditLogOutputSerializer},
        summary="Get audit log detail",
        description="Get a single audit log entry. ADMIN and AUDITOR only.",
        tags=["Audit"],
    )
    def get(self, request, log_id):
        log = audit_selector.get_audit_log_by_id(log_id=log_id)

        return Response(
            {
                "success": True,
                "message": "Audit log retrieved successfully",
                "data": AuditLogOutputSerializer(log).data,
                "errors": None,
            },
        )