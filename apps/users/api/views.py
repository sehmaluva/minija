"""User-related API views for registration, login, profile management, and permissions."""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import login, logout
from apps.users.models.models import User
from apps.users.api.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)


# The CookieTokenRefreshView is no longer needed.
# You can remove it and use the standard TokenRefreshView from simple_jwt in your urls.py
# like this: path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


class RegisterView(generics.CreateAPIView):
    """
    API view for user registration
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "message": "User registered successfully",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    API view for user login
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        login(request, user)

        refresh = RefreshToken.for_user(user)

        response_data = {
            "user": UserSerializer(user).data,
            "message": "Login successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(response_data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    API view for user logout.
    Client should handle token invalidation.
    Optionally, you can implement token blacklisting here.
    """
    try:
        # The following line is for Django's session-based authentication
        # and is not strictly necessary for a stateless JWT setup, but doesn't harm.
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for user profile
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "PUT" or self.request.method == "PATCH":
            return UserUpdateSerializer
        return UserSerializer


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """
    API view for changing password
    """
    serializer = ChangePasswordSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        # Create new JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Password changed successfully",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """
    API view for listing users (admin only)
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return User.objects.all()
        return User.objects.filter(id=user.id)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_permissions_view(request):
    """
    API view to get user permissions based on role
    """
    user = request.user
    permissions_map = {
        "admin": {
            "can_manage_users": True,
            "can_manage_farms": True,
            "can_manage_flocks": True,
            "can_manage_batches": True,
            "can_view_reports": True,
            "can_manage_health": True,
            "can_manage_production": True,
        },
        "user": {
            "can_manage_users": False,
            "can_manage_farms": True,
            "can_manage_flocks": True,
            "can_manage_batches": True,
            "can_view_reports": True,
            "can_manage_health": True,
            "can_manage_production": True,
        },
    }

    user_permissions = permissions_map.get(user.role, {})

    return Response(
        {"user": UserSerializer(user).data, "permissions": user_permissions},
        status=status.HTTP_200_OK,
    )
