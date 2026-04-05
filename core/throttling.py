from rest_framework.throttling import SimpleRateThrottle


class RoleBasedThrottle(SimpleRateThrottle):
    """Throttle requests based on user role."""

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

    def get_rate(self):
        if not hasattr(self, "request") or not self.request.user.is_authenticated:
            self.scope = "anon"
        else:
            self.scope = self.request.user.role
        return super().get_rate()

    def allow_request(self, request, view):
        self.request = request
        return super().allow_request(request, view)
