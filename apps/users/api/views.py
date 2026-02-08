"""User-related API views for registration, login, profile management, and permissions."""

import logging

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


# Module logger
logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.
    Creates user, sends 6-digit OTP + verification link email,
    and auto-creates a default organization.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        logger.info(
            "User registered: id=%s, email=%s",
            getattr(user, "id", None),
            getattr(user, "email", None),
        )

        return Response(
            {
                "user": UserSerializer(user).data,
                "message": "User registered successfully. Please check your email to verify your account.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class EmailVerificationView(generics.GenericAPIView):
    """
    Verify email via 6-digit OTP **code** (POST) or link **token** (GET).

    GET  /api/auth/verify-email/?token=<uuid>
    POST /api/auth/verify-email/  {"email": "...", "code": "123456"}
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        """Link-based verification (user clicked the email link)."""
        from apps.users.services.otp_service import verify_token

        token_str = request.query_params.get("token")
        if not token_str:
            return Response(
                {"error": "Token is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email_verification_token=token_str)
        except (User.DoesNotExist, Exception):
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )

        success, error = verify_token(user, token_str)
        if success:
            return Response(
                {"message": "Email successfully verified. You can now log in."},
                status=status.HTTP_200_OK,
            )
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        """Code-based verification (user entered 6-digit OTP in the app)."""
        from apps.users.services.otp_service import verify_otp

        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response(
                {"error": "Both email and code are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email."}, status=status.HTTP_400_BAD_REQUEST
            )

        success, error = verify_otp(user, code)
        if success:
            return Response(
                {"message": "Email successfully verified. You can now log in."},
                status=status.HTTP_200_OK,
            )
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailView(generics.GenericAPIView):
    """
    Resend the verification email with a fresh OTP code and link.
    Rate-limited to one email per cooldown period.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        from apps.users.services.otp_service import can_resend_otp, create_and_send_otp

        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal that the user does not exist
            return Response(
                {
                    "message": "If an account with this email exists, a verification email has been sent."
                },
                status=status.HTTP_200_OK,
            )

        if user.is_email_verified:
            return Response(
                {"message": "This email has already been verified."},
                status=status.HTTP_200_OK,
            )

        if not can_resend_otp(user):
            return Response(
                {"error": "Please wait before requesting a new code."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        create_and_send_otp(user, request)

        return Response(
            {"message": "A new verification email has been sent."},
            status=status.HTTP_200_OK,
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

        logger.info("Login successful for user id=%s", getattr(user, "id", None))

        return Response(response_data, status=status.HTTP_200_OK)
    # log a failed login attempt (avoid logging passwords)
    identifier = request.data.get("email") or request.data.get("username") or "unknown"
    logger.warning(
        "Login failed for identifier=%s; errors=%s", identifier, serializer.errors
    )

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
        logger.info("Logout called for user id=%s", getattr(request.user, "id", None))
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception("Error during logout: %s", str(e))
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

    def perform_update(self, serializer):
        serializer.save()
        logger.info(
            "Profile updated for user id=%s", getattr(self.request.user, "id", None)
        )


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
        logger.info("Password changed for user id=%s", getattr(user, "id", None))

        return Response(
            {
                "message": "Password changed successfully",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )

    logger.warning(
        "Password change failed for user id=%s; errors=%s",
        getattr(request.user, "id", None),
        serializer.errors,
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
        logger.debug("UserList requested by user id=%s", getattr(user, "id", None))
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

    logger.debug(
        "Permissions requested for user id=%s -> %s",
        getattr(user, "id", None),
        user_permissions,
    )

    return Response(
        {"user": UserSerializer(user).data, "permissions": user_permissions},
        status=status.HTTP_200_OK,
    )
