from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only ADMIN users."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsAdminOrAuditor(BasePermission):
    """ADMIN or AUDITOR users."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("admin", "auditor")
