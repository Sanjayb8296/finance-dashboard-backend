from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from core.models import SoftDeleteModel, TimestampedModel


class RecordType(models.TextChoices):
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"


class Category(models.TextChoices):
    SALARY = "salary", "Salary"
    FREELANCE = "freelance", "Freelance"
    INVESTMENTS = "investments", "Investments"
    RENT = "rent", "Rent"
    UTILITIES = "utilities", "Utilities"
    GROCERIES = "groceries", "Groceries"
    TRANSPORT = "transport", "Transport"
    ENTERTAINMENT = "entertainment", "Entertainment"
    HEALTHCARE = "healthcare", "Healthcare"
    EDUCATION = "education", "Education"
    SHOPPING = "shopping", "Shopping"
    TRAVEL = "travel", "Travel"
    INSURANCE = "insurance", "Insurance"
    TAXES = "taxes", "Taxes"
    OTHER = "other", "Other"


class FinancialRecord(TimestampedModel, SoftDeleteModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="financial_records",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    type = models.CharField(
        max_length=10,
        choices=RecordType.choices,
        db_index=True,
    )
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        db_index=True,
    )
    date = models.DateField(db_index=True)
    description = models.TextField(blank=True, default="")
    tags = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Comma-separated tags",
    )

    class Meta:
        db_table = "financial_records"
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "type"]),
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "category"]),
            models.Index(fields=["date", "type"]),
            models.Index(fields=["user", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.type} - {self.amount} ({self.category})"
