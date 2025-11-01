from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.users.models.models import User


@method_decorator(csrf_exempt, name="dispatch")
class CookieTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that handles refresh tokens from cookies
    """

    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie if not in request data
        refresh_token = request.data.get("refresh") or request.COOKIES.get(
            "refresh_token"
        )
        if refresh_token:
            request.data["refresh"] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Set new access token in cookie
            access_token = response.data.get("access")
            if access_token:
                response.set_cookie(
                    "access_token",
                    access_token,
                    httponly=True,
                    secure=False,  # Set to True in production with HTTPS
                    samesite="Lax",
                    max_age=1800,
                )

        return response


from django.contrib.auth import login, logout
from apps.users.models.models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)


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

        # Create JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response(
            {
                "user": UserSerializer(user).data,
                "message": "User registered successfully",
            },
            status=status.HTTP_201_CREATED,
        )

        # Set cookies
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="Lax",
            max_age=1800,
        )
        response.set_cookie(
            "refresh_token",
            str(refresh),
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="Lax",
            max_age=1800,
        )

        return response


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def login_view(request):
    """
    API view for user login
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        login(request, user)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response(
            {"user": UserSerializer(user).data, "message": "Login successful"},
            status=status.HTTP_200_OK,
        )

        # Set cookies
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="Lax",
            max_age=1800,
        )
        response.set_cookie(
            "refresh_token",
            str(refresh),
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="Lax",
            max_age=1800,
        )

        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
def logout_view(request):
    """
    API view for user logout
    """
    try:
        logout(request)
        response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

        # Clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
    except:
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
@csrf_exempt
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
        access_token = str(refresh.access_token)

        response = Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )

        # Update cookies with new tokens
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="Lax",
            max_age=1800,
        )
        response.set_cookie(
            "refresh_token",
            str(refresh),
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="Lax",
            max_age=1800,
        )

        return response

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
