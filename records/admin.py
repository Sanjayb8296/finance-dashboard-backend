from django.contrib import admin

from records.models import FinancialRecord


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount", "type", "category", "date", "is_deleted")
    list_filter = ("type", "category", "is_deleted")
    search_fields = ("description", "user__email")
    ordering = ("-date",)
