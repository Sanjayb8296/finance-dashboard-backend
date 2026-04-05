from decimal import Decimal

from rest_framework import serializers

from records.models import Category, FinancialRecord, RecordType
from users.api.serializers import UserMinimalSerializer


# --- Input Serializers ---


class RecordCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    type = serializers.ChoiceField(choices=RecordType.choices)
    category = serializers.ChoiceField(choices=Category.choices)
    date = serializers.DateField()
    description = serializers.CharField(required=False, default="")
    tags = serializers.CharField(required=False, default="")


class RecordUpdateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"), required=False)
    type = serializers.ChoiceField(choices=RecordType.choices, required=False)
    category = serializers.ChoiceField(choices=Category.choices, required=False)
    date = serializers.DateField(required=False)
    description = serializers.CharField(required=False)
    tags = serializers.CharField(required=False)


class BulkRecordCreateSerializer(serializers.Serializer):
    records = RecordCreateSerializer(many=True)

    def validate_records(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Maximum 100 records per batch")
        if len(value) == 0:
            raise serializers.ValidationError("At least one record is required")
        return value


# --- Output Serializers ---


class RecordOutputSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = FinancialRecord
        fields = [
            "id",
            "user",
            "amount",
            "type",
            "category",
            "date",
            "description",
            "tags",
            "created_at",
            "updated_at",
        ]
