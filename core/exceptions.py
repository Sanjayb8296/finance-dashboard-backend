from rest_framework import status
from rest_framework.exceptions import APIException


class ApplicationError(APIException):
    """Base exception for all application errors."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An application error occurred."


class PermissionDeniedError(ApplicationError):
    """Raised when user lacks permission for an action."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."


class NotFoundError(ApplicationError):
    """Raised when requested resource does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Requested resource not found."


class ValidationError(ApplicationError):
    """Raised for business logic validation failures."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation failed."


class ConflictError(ApplicationError):
    """Raised for duplicate or conflicting operations."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource conflict."
