import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def _get_error_message(exc):
    """Extract a human-readable error message from an exception."""
    if hasattr(exc, "detail"):
        detail = exc.detail
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list):
            return detail[0] if detail else str(exc)
        if isinstance(detail, dict):
            # For validation errors, return a generic message
            return "Validation failed"
    return str(exc)


def _get_error_details(exc):
    """Extract structured error details for the errors field."""
    if hasattr(exc, "detail"):
        detail = exc.detail
        if isinstance(detail, dict):
            return detail
    return None


def custom_exception_handler(exc, context):
    """Wrap all error responses in the consistent API format."""
    response = drf_exception_handler(exc, context)

    if response is not None:
        return Response(
            {
                "success": False,
                "message": _get_error_message(exc),
                "data": None,
                "errors": _get_error_details(exc),
            },
            status=response.status_code,
        )

    # Unhandled exceptions → 500
    logger.error("Unhandled exception", exc_info=exc)
    return Response(
        {
            "success": False,
            "message": "Internal server error",
            "data": None,
            "errors": None,
        },
        status=500,
    )
