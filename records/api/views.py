import csv

from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import StandardPagination
from records.api.serializers import (
    BulkRecordCreateSerializer,
    RecordCreateSerializer,
    RecordOutputSerializer,
    RecordUpdateSerializer,
)
from users.permissions.user_permissions import IsAdmin
from records.permissions.record_permissions import (
    CanCreateRecords,
    CanExportRecords,
    CanModifyRecords,
    CanViewRecords,
)
from records.selectors import record_selector
from records.services import record_service


class RecordListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), CanViewRecords()]
        return [IsAuthenticated(), CanCreateRecords()]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="type", enum=["income", "expense"], description="Filter by record type"),
            OpenApiParameter(name="category", description="Filter by category"),
            OpenApiParameter(name="date_from", type=str, description="Start date (YYYY-MM-DD)"),
            OpenApiParameter(name="date_to", type=str, description="End date (YYYY-MM-DD)"),
            OpenApiParameter(name="min_amount", type=float, description="Minimum amount"),
            OpenApiParameter(name="max_amount", type=float, description="Maximum amount"),
            OpenApiParameter(name="search", description="Search in description"),
            OpenApiParameter(name="tags", description="Filter by tags (comma-separated)"),
            OpenApiParameter(name="ordering", description="Order by field (e.g. -date, amount)"),
            OpenApiParameter(name="page", type=int, description="Page number"),
            OpenApiParameter(name="page_size", type=int, description="Page size"),
        ],
        responses={200: RecordOutputSerializer(many=True)},
        summary="List financial records",
        description="Returns paginated financial records filtered by role-based scoping.",
        tags=["Records"],
    )
    def get(self, request):
        records = record_selector.get_records(
            user=request.user,
            filters=request.query_params,
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(records, request)

        return paginator.get_paginated_response(
            RecordOutputSerializer(page, many=True).data,
        )

    @extend_schema(
        request=RecordCreateSerializer,
        responses={201: RecordOutputSerializer},
        summary="Create a financial record",
        description="Create a new financial record. MANAGER and ADMIN only.",
        tags=["Records"],
    )
    def post(self, request):
        serializer = RecordCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record = record_service.create_record(
            user=request.user,
            **serializer.validated_data,
        )

        return Response(
            {
                "success": True,
                "message": "Record created successfully",
                "data": RecordOutputSerializer(record).data,
                "errors": None,
            },
            status=status.HTTP_201_CREATED,
        )


class RecordDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), CanViewRecords()]
        return [IsAuthenticated(), CanModifyRecords()]

    @extend_schema(
        responses={200: RecordOutputSerializer},
        summary="Get record detail",
        description="Get a single financial record by ID.",
        tags=["Records"],
    )
    def get(self, request, record_id):
        record = record_selector.get_record_by_id(
            user=request.user,
            record_id=record_id,
        )

        return Response(
            {
                "success": True,
                "message": "Record retrieved successfully",
                "data": RecordOutputSerializer(record).data,
                "errors": None,
            },
        )

    @extend_schema(
        request=RecordUpdateSerializer,
        responses={200: RecordOutputSerializer},
        summary="Update record",
        description="Update a financial record. MANAGER (own only), ADMIN (any).",
        tags=["Records"],
    )
    def patch(self, request, record_id):
        serializer = RecordUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record = record_service.update_record(
            user=request.user,
            record_id=record_id,
            data=serializer.validated_data,
        )

        return Response(
            {
                "success": True,
                "message": "Record updated successfully",
                "data": RecordOutputSerializer(record).data,
                "errors": None,
            },
        )

    @extend_schema(
        responses={200: None},
        summary="Soft delete record",
        description="Soft delete a financial record. MANAGER (own only), ADMIN (any).",
        tags=["Records"],
    )
    def delete(self, request, record_id):
        record_service.soft_delete_record(
            user=request.user,
            record_id=record_id,
        )

        return Response(
            {
                "success": True,
                "message": "Record deleted successfully",
                "data": None,
                "errors": None,
            },
        )


class RecordExportView(APIView):
    permission_classes = [IsAuthenticated, CanExportRecords]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="type", enum=["income", "expense"], description="Filter by record type"),
            OpenApiParameter(name="category", description="Filter by category"),
            OpenApiParameter(name="date_from", type=str, description="Start date (YYYY-MM-DD)"),
            OpenApiParameter(name="date_to", type=str, description="End date (YYYY-MM-DD)"),
        ],
        responses={(200, "text/csv"): OpenApiTypes.BINARY},
        summary="Export records as CSV",
        description="Export financial records as CSV file. ANALYST, MANAGER, ADMIN, AUDITOR.",
        tags=["Records"],
    )
    def get(self, request):
        records = record_selector.get_records(
            user=request.user,
            filters=request.query_params,
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="financial_records.csv"'

        writer = csv.writer(response)
        writer.writerow(["ID", "User Email", "Amount", "Type", "Category", "Date", "Description", "Tags", "Created At"])

        for record in records:
            writer.writerow([
                record.id,
                record.user.email,
                record.amount,
                record.type,
                record.category,
                record.date,
                record.description,
                record.tags,
                record.created_at,
            ])

        return response


class RecordBulkCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        request=BulkRecordCreateSerializer,
        responses={201: RecordOutputSerializer(many=True)},
        summary="Bulk create records",
        description="Bulk create up to 100 financial records. ADMIN only.",
        tags=["Records"],
    )
    def post(self, request):
        serializer = BulkRecordCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        records = record_service.bulk_create_records(
            user=request.user,
            records_data=serializer.validated_data["records"],
        )

        return Response(
            {
                "success": True,
                "message": f"{len(records)} records created successfully",
                "data": RecordOutputSerializer(records, many=True).data,
                "errors": None,
            },
            status=status.HTTP_201_CREATED,
        )
