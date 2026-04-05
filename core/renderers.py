from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):
    """Wrap all successful responses in the standard envelope format."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None

        # If already wrapped (e.g. by exception handler), pass through
        if isinstance(data, dict) and "success" in data:
            return super().render(data, accepted_media_type, renderer_context)

        if response and response.status_code >= 400:
            # Error responses are handled by the exception handler
            return super().render(data, accepted_media_type, renderer_context)

        wrapped = {
            "success": True,
            "message": "Success",
            "data": data,
            "errors": None,
        }

        return super().render(wrapped, accepted_media_type, renderer_context)
