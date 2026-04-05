try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None


class SentryUserContextMiddleware:
    """Attach user info to Sentry events for debugging."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if sentry_sdk and hasattr(request, "user") and request.user.is_authenticated:
            sentry_sdk.set_user(
                {
                    "id": request.user.id,
                    "email": request.user.email,
                    "role": request.user.role,
                }
            )
        response = self.get_response(request)
        return response
