from django.db import models


class AuditAction(models.TextChoices):
    CREATE = "create", "Create"
    UPDATE = "update", "Update"
    DELETE = "delete", "Delete"
    RESTORE = "restore", "Restore"
    LOGIN = "login", "Login"
    LOGOUT = "logout", "Logout"
    PERMISSION_DENIED = "permission_denied", "Permission Denied"
    ROLE_CHANGE = "role_change", "Role Change"
    EXPORT = "export", "Export"


class AuditLog(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=30, choices=AuditAction.choices)
    resource_type = models.CharField(max_length=50)
    resource_id = models.PositiveIntegerField(null=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "action"]),
            models.Index(fields=["resource_type", "resource_id"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.resource_type}:{self.resource_id}"
