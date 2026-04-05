from django.db import connection
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: inline_serializer(
            name="HealthCheckResponse",
            fields={
                "status": serializers.CharField(),
                "database": serializers.CharField(),
                "timestamp": serializers.DateTimeField(),
            },
        )},
        summary="Health check",
        description="Check system health and database connectivity.",
        tags=["System"],
    )
    def get(self, request):
        # Check database
        try:
            connection.ensure_connection()
            db_status = "connected"
        except Exception:
            db_status = "disconnected"

        return Response(
            {
                "success": True,
                "message": "System healthy",
                "data": {
                    "status": "healthy" if db_status == "connected" else "degraded",
                    "database": db_status,
                    "timestamp": timezone.now().isoformat(),
                },
                "errors": None,
            },
        )
