from django.urls import path

from users.api.views import (
    LoginView,
    LogoutView,
    ProfileView,
    RefreshView,
    RegisterView,
    UserDetailView,
    UserListCreateView,
)

urlpatterns = [
    # Auth
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    # Profile
    path("users/me/", ProfileView.as_view(), name="user-profile"),
    # User management
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:user_id>/", UserDetailView.as_view(), name="user-detail"),
]
