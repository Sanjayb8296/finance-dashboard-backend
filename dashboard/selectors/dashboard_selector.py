from datetime import date
from decimal import Decimal

from django.db.models import Avg, Count, DecimalField, Max, Q, Sum, Value
from django.db.models.functions import Coalesce, TruncMonth

from records.models import FinancialRecord
from users.models import Role, User


def _get_base_queryset(*, user: User) -> "QuerySet[FinancialRecord]":
    """Get base queryset with role-based scoping."""
    qs = FinancialRecord.objects.select_related("user")
    if user.role in (Role.VIEWER, Role.MANAGER):
        qs = qs.filter(user=user)
    return qs


def get_summary(
    *,
    user: User,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict:
    """Get dashboard financial summary using DB-level aggregations."""
    qs = _get_base_queryset(user=user)

    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    zero = Value(Decimal("0.00"), output_field=DecimalField())

    result = qs.aggregate(
        total_income=Coalesce(Sum("amount", filter=Q(type="income")), zero),
        total_expense=Coalesce(Sum("amount", filter=Q(type="expense")), zero),
        record_count=Count("id"),
        avg_transaction=Coalesce(Avg("amount"), zero),
        largest_income=Coalesce(Max("amount", filter=Q(type="income")), zero),
        largest_expense=Coalesce(Max("amount", filter=Q(type="expense")), zero),
    )

    result["net_balance"] = result["total_income"] - result["total_expense"]

    return result


def get_trends(*, user: User, months: int = 12) -> list[dict]:
    """Get monthly income/expense trends using DB-level aggregations."""
    qs = _get_base_queryset(user=user)

    zero = Value(Decimal("0.00"), output_field=DecimalField())

    trends = (
        qs.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(
            income=Coalesce(Sum("amount", filter=Q(type="income")), zero),
            expense=Coalesce(Sum("amount", filter=Q(type="expense")), zero),
            transaction_count=Count("id"),
        )
        .order_by("-month")[:months]
    )

    result = []
    for t in trends:
        result.append(
            {
                "month": t["month"].strftime("%Y-%m"),
                "income": t["income"],
                "expense": t["expense"],
                "net": t["income"] - t["expense"],
                "transaction_count": t["transaction_count"],
            }
        )

    return result


def get_category_breakdown(
    *,
    user: User,
    type_filter: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict:
    """Get category-wise totals with percentages."""
    qs = _get_base_queryset(user=user)

    if type_filter:
        qs = qs.filter(type=type_filter)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    breakdown = (
        qs.values("category")
        .annotate(
            total=Sum("amount"),
            count=Count("id"),
        )
        .order_by("-total")
    )

    grand_total = sum(item["total"] for item in breakdown) if breakdown else Decimal("0.00")

    result = []
    for item in breakdown:
        percentage = (
            (item["total"] / grand_total * 100).quantize(Decimal("0.01"))
            if grand_total > 0
            else Decimal("0.00")
        )
        result.append(
            {
                "category": item["category"],
                "total": item["total"],
                "count": item["count"],
                "percentage": percentage,
            }
        )

    return {"breakdown": result, "grand_total": grand_total}


def get_recent_transactions(*, user: User, limit: int = 10) -> list:
    """Get recent transactions."""
    qs = _get_base_queryset(user=user).order_by("-date", "-created_at")[:limit]
    return list(qs)
