from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import NotFoundError
from users.api.serializers import (
    LoginSerializer,
    LoginOutputSerializer,
    ProfileUpdateSerializer,
    RefreshSerializer,
    RegisterSerializer,
    UserCreateSerializer,
    UserOutputSerializer,
    UserUpdateSerializer,
)
from users.permissions.user_permissions import IsAdmin, IsAdminOrAuditor
from users.selectors import user_selector
from users.services import user_service


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserOutputSerializer},
        summary="Register a new user",
        description="Register a new user with default VIEWER role.",
        tags=["Auth"],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_service.register_user(
            email=serializer.validated_data["email"],
            name=serializer.validated_data["name"],
            password=serializer.validated_data["password"],
        )

        return Response(
            {
                "success": True,
                "message": "User registered successfully",
                "data": UserOutputSerializer(user).data,
                "errors": None,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: None},
        summary="Login",
        description="Authenticate and receive JWT token pair.",
        tags=["Auth"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_service.authenticate_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        tokens = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "message": "Login successful",
                "data": {
                    "access": str(tokens.access_token),
                    "refresh": str(tokens),
                    "user": UserOutputSerializer(user).data,
                },
                "errors": None,
            },
            status=status.HTTP_200_OK,
        )


class RefreshView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RefreshSerializer,
        responses={200: inline_serializer(
            name="RefreshResponse",
            fields={
                "access": serializers.CharField(),
                "refresh": serializers.CharField(),
            },
        )},
        summary="Refresh access token",
        description="Get a new access token using a refresh token.",
        tags=["Auth"],
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {
                    "success": False,
                    "message": "Refresh token is required",
                    "data": None,
                    "errors": {"refresh": ["This field is required."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            return Response(
                {
                    "success": True,
                    "message": "Token refreshed successfully",
                    "data": {
                        "access": str(token.access_token),
                        "refresh": str(token),
                    },
                    "errors": None,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {
                    "success": False,
                    "message": "Token is invalid or expired",
                    "data": None,
                    "errors": None,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=RefreshSerializer,
        responses={200: None},
        summary="Logout",
        description="Blacklist the refresh token.",
        tags=["Auth"],
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {
                    "success": False,
                    "message": "Refresh token is required",
                    "data": None,
                    "errors": {"refresh": ["This field is required."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass

        return Response(
            {
                "success": True,
                "message": "Logged out successfully",
                "data": None,
                "errors": None,
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserOutputSerializer},
        summary="Get current user profile",
        description="Get the authenticated user's profile.",
        tags=["Users"],
    )
    def get(self, request):
        return Response(
            {
                "success": True,
                "message": "Profile retrieved successfully",
                "data": UserOutputSerializer(request.user).data,
                "errors": None,
            },
        )

    @extend_schema(
        request=ProfileUpdateSerializer,
        responses={200: UserOutputSerializer},
        summary="Update own profile",
        description="Update the authenticated user's profile (name only).",
        tags=["Users"],
    )
    def patch(self, request):
        serializer = ProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_service.update_profile(
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            {
                "success": True,
                "message": "Profile updated successfully",
                "data": UserOutputSerializer(user).data,
                "errors": None,
            },
        )


class UserListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), IsAdminOrAuditor()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="role", description="Filter by role"),
            OpenApiParameter(name="is_active", description="Filter by active status"),
            OpenApiParameter(name="search", description="Search by email or name"),
            OpenApiParameter(name="page", type=int, description="Page number"),
        ],
        responses={200: UserOutputSerializer(many=True)},
        summary="List all users",
        description="List all users. ADMIN and AUDITOR only.",
        tags=["Users"],
    )
    def get(self, request):
        from core.pagination import StandardPagination

        users = user_selector.get_users(filters=request.query_params)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(users, request)

        return paginator.get_paginated_response(
            UserOutputSerializer(page, many=True).data,
        )

    @extend_schema(
        request=UserCreateSerializer,
        responses={201: UserOutputSerializer},
        summary="Create a new user",
        description="Create a new user. ADMIN only.",
        tags=["Users"],
    )
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_service.create_user(
            admin=request.user,
            email=serializer.validated_data["email"],
            name=serializer.validated_data["name"],
            password=serializer.validated_data["password"],
            role=serializer.validated_data.get("role", "viewer"),
        )

        return Response(
            {
                "success": True,
                "message": "User created successfully",
                "data": UserOutputSerializer(user).data,
                "errors": None,
            },
            status=status.HTTP_201_CREATED,
        )


class UserDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), IsAdminOrAuditor()]
        return [IsAuthenticated(), IsAdmin()]

    @extend_schema(
        responses={200: UserOutputSerializer},
        summary="Get user detail",
        description="Get user detail. ADMIN and AUDITOR only.",
        tags=["Users"],
    )
    def get(self, request, user_id):
        user = user_selector.get_user_by_id(user_id=user_id)
        if not user:
            raise NotFoundError("User not found")

        return Response(
            {
                "success": True,
                "message": "User retrieved successfully",
                "data": UserOutputSerializer(user).data,
                "errors": None,
            },
        )

    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserOutputSerializer},
        summary="Update user",
        description="Update user (name, role, is_active). ADMIN only.",
        tags=["Users"],
    )
    def patch(self, request, user_id):
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_service.update_user(
            admin=request.user,
            user_id=user_id,
            data=serializer.validated_data,
        )

        return Response(
            {
                "success": True,
                "message": "User updated successfully",
                "data": UserOutputSerializer(user).data,
                "errors": None,
            },
        )

    @extend_schema(
        responses={200: UserOutputSerializer},
        summary="Deactivate user",
        description="Deactivate user (sets is_active=false). ADMIN only.",
        tags=["Users"],
    )
    def delete(self, request, user_id):
        user = user_service.deactivate_user(
            admin=request.user,
            user_id=user_id,
        )

        return Response(
            {
                "success": True,
                "message": "User deactivated successfully",
                "data": UserOutputSerializer(user).data,
                "errors": None,
            },
        )
