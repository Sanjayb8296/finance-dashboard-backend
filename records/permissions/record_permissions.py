from rest_framework.permissions import BasePermission


class CanViewRecords(BasePermission):
    """ANALYST, MANAGER, ADMIN, AUDITOR can view records."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "analyst",
            "manager",
            "admin",
            "auditor",
        )


class CanCreateRecords(BasePermission):
    """MANAGER, ADMIN can create records."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "manager",
            "admin",
        )


class CanModifyRecords(BasePermission):
    """MANAGER (own), ADMIN (any) can update/delete records."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "manager",
            "admin",
        )


class CanExportRecords(BasePermission):
    """ANALYST, MANAGER, ADMIN, AUDITOR can export."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "analyst",
            "manager",
            "admin",
            "auditor",
        )
