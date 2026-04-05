from rest_framework import serializers

from audit.models import AuditLog
from users.api.serializers import UserMinimalSerializer


class AuditLogOutputSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "action",
            "resource_type",
            "resource_id",
            "changes",
            "ip_address",
            "user_agent",
            "timestamp",
        ]
