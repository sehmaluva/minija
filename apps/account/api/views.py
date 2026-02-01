"""DRF API Views for Account Management"""

from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import base36_to_int, int_to_base36
from django.utils.translation import gettext_lazy as _
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.account.signals import signals
from apps.account.conf import settings
from apps.account.hooks import hookset
from apps.account.models.models import (
    Account,
    AccountDeletion,
    EmailAddress,
    EmailConfirmation,
    PasswordHistory,
    SignupCode,
)
from apps.account.api.serializers import (
    SignupSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    AccountSettingsSerializer,
    EmailConfirmationSerializer,
    AccountDeletionSerializer,
    ResendEmailVerificationSerializer,
    UserSerializer,
)

User = get_user_model()


# ==================== REGISTER API VIEW ====================


class RegisterAPIView(generics.CreateAPIView):
    """
    API view for user registration.

    POST /api/auth/register/
    {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "code": "optional-signup-code"
    }

    Returns:
        - User data with JWT tokens if successful
        - Email confirmation message if email verification required
        - Approval message if admin approval required
    """

    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        # Check if signup is open
        code = request.data.get("code")
        signup_code = None

        if code:
            try:
                signup_code = SignupCode.check_code(code)
            except SignupCode.InvalidCode:
                return Response(
                    {"error": f"The code {code} is invalid."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not signup_code and not settings.ACCOUNT_OPEN_SIGNUP:
            return Response(
                {"error": "Signup is currently closed."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Validate data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create user
        created_user = self.perform_create(serializer, signup_code)

        # Emit signup signal
        signals.user_signed_up.send(sender=self.__class__, user=created_user, form=None)

        # Handle different scenarios
        if settings.ACCOUNT_APPROVAL_REQUIRED:
            created_user.is_active = False
            created_user.save()
            return Response(
                {
                    "message": "Your account has been created and is pending approval.",
                    "email": created_user.email,
                },
                status=status.HTTP_201_CREATED,
            )

        # Get email address
        email_address = EmailAddress.objects.filter(
            user=created_user, primary=True
        ).first()

        if (
            settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED
            and email_address
            and not email_address.verified
        ):
            return Response(
                {
                    "message": "Registration successful. Please check your email to verify your account.",
                    "email": created_user.email,
                },
                status=status.HTTP_201_CREATED,
            )

        # Auto-login and return JWT tokens
        user_data = UserSerializer(created_user).data
        refresh = RefreshToken.for_user(created_user)

        return Response(
            {
                "user": user_data,
                "message": "Registration successful.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer, signup_code=None):
        """
        Create user with all related objects:
        - User
        - Account (timezone, language)
        - EmailAddress
        - EmailConfirmation (if required)
        - PasswordHistory (if enabled)
        - SignupCodeResult (if code used)
        """
        validated_data = serializer.validated_data

        # Create user
        user = User(
            username=validated_data["username"], email=validated_data["email"].strip()
        )
        user.set_password(validated_data["password"])

        # Set inactive if email confirmation required
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED:
            user.is_active = False

        # Prevent Account post_save signal from creating Account
        user._disable_account_creation = True
        user.save()

        # Use signup code if provided
        if signup_code:
            signup_code.use(user)

        # Create EmailAddress
        email_verified = False
        if signup_code and signup_code.email:
            email_verified = user.email == signup_code.email

        email_address = EmailAddress.objects.add_email(
            user, user.email, primary=True, verified=email_verified
        )

        # Create Account with timezone/language
        Account.create(request=self.request, user=user, create_email=False)

        # Create password history if enabled
        if settings.ACCOUNT_PASSWORD_USE_HISTORY:
            PasswordHistory.objects.create(
                user=user, password=make_password(validated_data["password"])
            )

        # Send email confirmation if needed
        if settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL and not email_address.verified:
            email_address.send_confirmation(site=get_current_site(self.request))

        # Set user inactive if email confirmation required and not verified
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED and not email_address.verified:
            user.is_active = False
            user.save()

        return user


# ==================== LOGIN API VIEW ====================


class LoginAPIView(APIView):
    """
    API view for user login with JWT authentication.

    POST /api/auth/login/
    {
        "username": "johndoe",  // or "email": "john@example.com"
        "password": "SecurePass123!",
        "remember": true
    }

    Returns JWT access and refresh tokens with user data.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            # Emit login attempt failure signal
            identifier = (
                request.data.get("username") or request.data.get("email") or "unknown"
            )
            signals.user_login_attempt.send(
                sender=self.__class__, username=identifier, result=False
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get authenticated user from validated data
        user = serializer.validated_data["user"]
        remember = serializer.validated_data.get("remember", False)

        # Login user (creates session)
        auth.login(request, user)

        # Set session expiry based on remember me
        expiry = settings.ACCOUNT_REMEMBER_ME_EXPIRY if remember else 0
        request.session.set_expiry(expiry)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Emit login success signal
        signals.user_logged_in.send(sender=self.__class__, user=user, form=None)

        # Prepare user data
        user_data = UserSerializer(user).data

        return Response(
            {
                "user": user_data,
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


# ==================== LOGOUT API VIEW ====================


class LogoutAPIView(APIView):
    """
    API view for user logout.

    POST /api/auth/logout/
    {
        "refresh": "refresh_token_here"  // optional, to blacklist token
    }

    Logs out user and optionally blacklists refresh token.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Blacklist refresh token if provided
        refresh_token = request.data.get("refresh")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass  # Token already invalid or blacklisted

        # Logout user (clear session)
        auth.logout(request)

        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


# ==================== CONFIRM EMAIL API VIEW ====================


class ConfirmEmailAPIView(APIView):
    """
    API view for email confirmation.

    POST /api/auth/confirm-email/
    {
        "key": "confirmation-key-here"
    }

    Verifies email address and optionally auto-logs in user.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailConfirmationSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get confirmation from context (set in serializer validation)
        confirmation = serializer.context.get("confirmation")

        # Confirm email
        email_address = confirmation.confirm()

        if not email_address:
            return Response(
                {"error": "Email confirmation failed or already confirmed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Activate user
        user = email_address.user
        user.is_active = True
        user.save()

        response_data = {
            "message": f"You have confirmed {email_address.email}.",
            "email": email_address.email,
        }

        # Auto-login if enabled
        if settings.ACCOUNT_EMAIL_CONFIRMATION_AUTO_LOGIN:
            user.backend = "django.contrib.auth.backends.ModelBackend"
            auth.login(request, user)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            response_data["refresh"] = str(refresh)
            response_data["access"] = str(refresh.access_token)
            response_data["user"] = UserSerializer(user).data

        return Response(response_data, status=status.HTTP_200_OK)


# ==================== CHANGE PASSWORD API VIEW ====================


class ChangePasswordAPIView(APIView):
    """
    API view for authenticated user password change.

    POST /api/auth/password/change/
    {
        "password_current": "OldPass123!",
        "password_new": "NewPass456!",
        "password_new_confirm": "NewPass456!"
    }

    Changes password and optionally creates password history.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        new_password = serializer.validated_data["password_new"]

        # Change password
        user.set_password(new_password)
        user.save()

        # Update session auth hash to keep user logged in
        auth.update_session_auth_hash(request, user)

        # Create password history if enabled
        if settings.ACCOUNT_PASSWORD_USE_HISTORY:
            PasswordHistory.objects.create(
                user=user, password=make_password(new_password)
            )

        # Emit password changed signal
        signals.password_changed.send(sender=self.__class__, user=user)

        # Send password change notification email if enabled
        if settings.ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE:
            protocol = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
            current_site = get_current_site(request)
            ctx = {
                "user": user,
                "protocol": protocol,
                "current_site": current_site,
            }
            hookset.send_password_change_email([user.email], ctx)

        return Response(
            {"message": "Password successfully changed."}, status=status.HTTP_200_OK
        )


# ==================== PASSWORD RESET REQUEST API VIEW ====================


class PasswordResetRequestAPIView(APIView):
    """
    API view for requesting password reset.

    POST /api/auth/password/reset/
    {
        "email": "john@example.com"
    }

    Sends password reset email to all users with that email address.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        # Send reset emails to all users with this email
        self.send_reset_email(email)

        return Response(
            {"message": "Password reset email has been sent."},
            status=status.HTTP_200_OK,
        )

    def send_reset_email(self, email):
        """Send password reset email to all users with this email."""
        protocol = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
        current_site = get_current_site(self.request)
        email_qs = EmailAddress.objects.filter(email__iexact=email)

        for user in User.objects.filter(pk__in=email_qs.values("user")):
            uid = int_to_base36(user.id)
            token = default_token_generator.make_token(user)

            # Build reset URL (should point to your frontend)
            # Format: https://yourdomain.com/password-reset/{uid}/{token}
            password_reset_url = (
                f"{protocol}://{current_site.domain}/password-reset/{uid}/{token}"
            )

            ctx = {
                "user": user,
                "current_site": current_site,
                "password_reset_url": password_reset_url,
                "uid": uid,
                "token": token,
            }
            hookset.send_password_reset_email([email], ctx)


# ==================== PASSWORD RESET CONFIRM API VIEW ====================


class PasswordResetConfirmAPIView(APIView):
    """
    API view for confirming password reset with token.

    POST /api/auth/password/reset/confirm/
    {
        "uidb36": "base36-user-id",
        "token": "reset-token",
        "password": "NewPass123!",
        "password_confirm": "NewPass123!"
    }

    Validates token and sets new password.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uidb36 = serializer.validated_data["uidb36"]
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        # Get user from uidb36
        try:
            uid_int = base36_to_int(uidb36)
            user = User.objects.get(id=uid_int)
        except (ValueError, User.DoesNotExist):
            return Response(
                {"error": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate token
        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Change password
        user.set_password(password)
        user.save()

        # Create password history if enabled
        if settings.ACCOUNT_PASSWORD_USE_HISTORY:
            PasswordHistory.objects.create(user=user, password=make_password(password))

        # Emit password changed signal
        signals.password_changed.send(sender=self.__class__, user=user)

        # Send password change notification if enabled
        if settings.ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE:
            protocol = settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL
            current_site = get_current_site(request)
            ctx = {
                "user": user,
                "protocol": protocol,
                "current_site": current_site,
            }
            hookset.send_password_change_email([user.email], ctx)

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


# ==================== ACCOUNT SETTINGS API VIEW ====================


class AccountSettingsAPIView(generics.RetrieveUpdateAPIView):
    """
    API view for account settings.

    GET /api/auth/settings/
    Returns current settings (email, timezone, language)

    PUT/PATCH /api/auth/settings/
    {
        "email": "newemail@example.com",
        "timezone": "America/New_York",
        "language": "en"
    }

    Updates account settings and optionally sends email confirmation.
    """

    serializer_class = AccountSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return current user's settings."""
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        """Get current settings."""
        user = request.user
        primary_email = EmailAddress.objects.get_primary(user)

        data = {
            "email": primary_email.email if primary_email else user.email,
            "timezone": user.account.timezone if hasattr(user, "account") else "",
            "language": user.account.language if hasattr(user, "account") else "",
        }

        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """Update settings."""
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        validated_data = serializer.validated_data

        # Update email
        self.update_email(user, validated_data.get("email"))

        # Update account (timezone, language)
        self.update_account(user, validated_data)

        return Response(
            {"message": "Account settings updated successfully."},
            status=status.HTTP_200_OK,
        )

    def update_email(self, user, email):
        """Update user's primary email."""
        if not email:
            return

        email = email.strip()
        primary_email = EmailAddress.objects.get_primary(user)
        confirm = settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL

        if not primary_email:
            # Create new primary email
            user.email = email
            EmailAddress.objects.add_email(user, email, primary=True, confirm=confirm)
            user.save()
        else:
            # Change existing email if different
            if email != primary_email.email:
                primary_email.change(email, confirm=confirm)

    def update_account(self, user, validated_data):
        """Update account timezone and language."""
        if not hasattr(user, "account"):
            return

        account = user.account
        updated = False

        if "timezone" in validated_data and validated_data["timezone"]:
            account.timezone = validated_data["timezone"]
            updated = True

        if "language" in validated_data and validated_data["language"]:
            account.language = validated_data["language"]
            updated = True

        if updated:
            account.save()


# ==================== ACCOUNT DELETE API VIEW ====================


class AccountDeleteAPIView(APIView):
    """
    API view for account deletion (soft delete).

    POST /api/auth/delete/
    {
        "password": "CurrentPass123!"
    }

    Marks account for deletion with expunge delay.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AccountDeletionSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        # Mark account for deletion
        AccountDeletion.mark(user)

        # Logout user
        auth.logout(request)

        return Response(
            {
                "message": f"Your account is now inactive and your data will be expunged in the next {settings.ACCOUNT_DELETION_EXPUNGE_HOURS} hours.",
                "expunge_hours": settings.ACCOUNT_DELETION_EXPUNGE_HOURS,
            },
            status=status.HTTP_200_OK,
        )


# ==================== RESEND EMAIL VERIFICATION API VIEW ====================


class ResendEmailVerificationAPIView(APIView):
    """
    API view for resending email verification.

    POST /api/auth/resend-verification/
    {
        "email": "john@example.com"
    }

    Resends verification email if email exists and is not verified.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ResendEmailVerificationSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get email_address from context (set in serializer validation)
        email_address = serializer.context.get("email_address")

        # Send confirmation email
        email_address.send_confirmation(site=get_current_site(request))

        return Response(
            {"message": f"Verification email sent to {email_address.email}."},
            status=status.HTTP_200_OK,
        )
