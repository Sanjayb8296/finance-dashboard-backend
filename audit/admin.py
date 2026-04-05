from django.contrib import admin

from audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action", "resource_type", "resource_id", "timestamp")
    list_filter = ("action", "resource_type")
    search_fields = ("user__email",)
    ordering = ("-timestamp",)
    readonly_fields = ("user", "action", "resource_type", "resource_id", "changes", "ip_address", "user_agent", "timestamp")
