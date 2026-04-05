from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    record_count = serializers.IntegerField()
    avg_transaction = serializers.DecimalField(max_digits=14, decimal_places=2)
    largest_income = serializers.DecimalField(max_digits=14, decimal_places=2)
    largest_expense = serializers.DecimalField(max_digits=14, decimal_places=2)


class TrendItemSerializer(serializers.Serializer):
    month = serializers.CharField()
    income = serializers.DecimalField(max_digits=14, decimal_places=2)
    expense = serializers.DecimalField(max_digits=14, decimal_places=2)
    net = serializers.DecimalField(max_digits=14, decimal_places=2)
    transaction_count = serializers.IntegerField()


class CategoryBreakdownItemSerializer(serializers.Serializer):
    category = serializers.CharField()
    total = serializers.DecimalField(max_digits=14, decimal_places=2)
    count = serializers.IntegerField()
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
