from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from core.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    # API v1
    path("api/v1/", include("users.api.urls")),
    path("api/v1/", include("records.api.urls")),
    path("api/v1/", include("dashboard.api.urls")),
    path("api/v1/", include("audit.api.urls")),
    # System
    path("api/v1/health/", HealthCheckView.as_view(), name="health-check"),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
