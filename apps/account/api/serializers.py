"""Serializers for Account app API."""

import re
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.account.conf import settings
from apps.account.hooks import hookset
from apps.account.models.models import (
    Account,
    EmailAddress,
    EmailConfirmation,
    SignupCode,
    PasswordHistory,
)
from apps.account.utils.utils import get_user_lookup_kwargs

User = get_user_model()

# Regex for username validation (alphanumeric + . / + / - / _)
alnum_re = re.compile(r"^[\w\-\.\+]+$")

# Get max length for username field
USER_FIELD_MAX_LENGTH = getattr(User, User.USERNAME_FIELD).field.max_length


# ==================== READ-ONLY SERIALIZERS ====================


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Account model (timezone, language)"""

    class Meta:
        model = Account
        fields = ["timezone", "language"]
        read_only_fields = ["timezone", "language"]


class EmailAddressSerializer(serializers.ModelSerializer):
    """Serializer for EmailAddress model"""

    class Meta:
        model = EmailAddress
        fields = ["id", "email", "verified", "primary"]
        read_only_fields = ["id", "email", "verified", "primary"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with nested account"""

    account = AccountSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "account",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "account",
        ]


# ==================== SIGNUP SERIALIZER ====================


class SignupSerializer(serializers.Serializer):
    """
    Serializer for user registration.

    Validates username uniqueness, email uniqueness (if required),
    password confirmation match, and optional signup code.
    """

    username = serializers.CharField(
        max_length=USER_FIELD_MAX_LENGTH,
        required=True,
        help_text="Username for the account",
    )
    email = serializers.EmailField(
        required=True, help_text="Email address for the account"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="Password for the account",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="Password confirmation",
    )
    code = serializers.CharField(
        max_length=64,
        required=False,
        allow_blank=True,
        help_text="Optional signup/invitation code",
    )

    def validate_username(self, value):
        """Validate username pattern and uniqueness"""
        if not alnum_re.search(value):
            raise serializers.ValidationError(
                "Usernames can only contain letters, numbers and ./+/-/_"
            )

        lookup_kwargs = get_user_lookup_kwargs(
            {f"{User.USERNAME_FIELD}__iexact": value}
        )
        qs = User.objects.filter(**lookup_kwargs)
        if qs.exists():
            raise serializers.ValidationError(
                "This username is already taken. Please choose another."
            )

        return value

    def validate_email(self, value):
        """Validate email uniqueness"""
        value = value.strip().lower()
        qs = EmailAddress.objects.filter(email__iexact=value)

        if qs.exists() and settings.ACCOUNT_EMAIL_UNIQUE:
            raise serializers.ValidationError(
                "A user is registered with this email address."
            )

        return value

    def validate_code(self, value):
        """Validate signup code if provided"""
        if value:
            try:
                signup_code = SignupCode.check_code(value)
                self.context["signup_code"] = signup_code
                return value
            except SignupCode.InvalidCode:
                raise serializers.ValidationError(f"The code {value} is invalid.")
        return value

    def validate(self, attrs):
        """Cross-field validation for passwords"""
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "You must type the same password each time."}
            )

        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs


# ==================== LOGIN SERIALIZER ====================


class LoginSerializer(serializers.Serializer):
    """Serializer for user login with JWT"""

    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    remember = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        """Authenticate user"""
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")

        if not username and not email:
            raise serializers.ValidationError("Must provide either username or email.")

        identifier = username or email

        credentials = hookset.get_user_credentials(
            {"cleaned_data": {"username": identifier, "password": password}}, "username"
        )

        user = authenticate(**credentials)

        if not user:
            raise serializers.ValidationError(
                "The username/email and/or password you specified are not correct."
            )

        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

        attrs["user"] = user
        return attrs


# ==================== CHANGE PASSWORD SERIALIZER ====================


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""

    password_current = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password_new = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password_new_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate_password_current(self, value):
        """Verify current password"""
        user = self.context.get("request").user

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated.")

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Please type your current password correctly."
            )

        return value

    def validate(self, attrs):
        """Validate new passwords match and are strong"""
        password_new = attrs.get("password_new")
        password_new_confirm = attrs.get("password_new_confirm")
        password_current = attrs.get("password_current")

        try:
            hookset.clean_password(password_new, password_new_confirm)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password_new_confirm": str(e.message)})

        user = self.context.get("request").user
        try:
            validate_password(password_new, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password_new": list(e.messages)})

        if password_new == password_current:
            raise serializers.ValidationError(
                {
                    "password_new": "New password must be different from current password."
                }
            )

        return attrs


# ==================== PASSWORD RESET SERIALIZERS ====================


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset"""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate email exists"""
        value = value.strip().lower()

        if not EmailAddress.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email address cannot be found.")

        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset"""

    uidb36 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        """Validate passwords match"""
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        try:
            hookset.clean_password(password, password_confirm)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password_confirm": str(e.message)})

        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs


# ==================== ACCOUNT SETTINGS SERIALIZER ====================


class AccountSettingsSerializer(serializers.Serializer):
    """Serializer for account settings update"""

    email = serializers.EmailField(required=True)
    timezone = serializers.ChoiceField(
        choices=settings.ACCOUNT_TIMEZONES, required=False, allow_blank=True
    )
    language = serializers.ChoiceField(
        choices=settings.ACCOUNT_LANGUAGES, required=False, allow_blank=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.USE_I18N:
            self.fields.pop("language", None)

    def validate_email(self, value):
        """Validate email uniqueness if changed"""
        value = value.strip().lower()
        user = self.context.get("request").user

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated.")

        try:
            primary_email = EmailAddress.objects.get_primary(user)
            current_email = primary_email.email.lower() if primary_email else None
        except EmailAddress.DoesNotExist:
            current_email = None

        if current_email and value == current_email:
            return value

        qs = EmailAddress.objects.filter(email__iexact=value)
        if qs.exists() and settings.ACCOUNT_EMAIL_UNIQUE:
            raise serializers.ValidationError(
                "A user is registered with this email address."
            )

        return value


# ==================== EMAIL CONFIRMATION SERIALIZER ====================


class EmailConfirmationSerializer(serializers.Serializer):
    """Serializer for email confirmation"""

    key = serializers.CharField(required=True)

    def validate_key(self, value):
        """Validate confirmation key"""
        try:
            confirmation = EmailConfirmation.objects.select_related(
                "email_address__user"
            ).get(key=value.lower())
        except EmailConfirmation.DoesNotExist:
            raise serializers.ValidationError("Invalid confirmation key.")

        if confirmation.key_expired():
            raise serializers.ValidationError("Email confirmation has expired.")

        self.context["confirmation"] = confirmation
        return value


# ==================== ACCOUNT DELETION SERIALIZER ====================


class AccountDeletionSerializer(serializers.Serializer):
    """Serializer for account deletion"""

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate_password(self, value):
        """Verify password before deletion"""
        user = self.context.get("request").user

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated.")

        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect password.")

        return value


# ==================== RESEND EMAIL VERIFICATION SERIALIZER ====================


class ResendEmailVerificationSerializer(serializers.Serializer):
    """Serializer for resending email verification"""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate email exists and not verified"""
        value = value.strip().lower()

        try:
            email_address = EmailAddress.objects.get(email__iexact=value)
        except EmailAddress.DoesNotExist:
            raise serializers.ValidationError("Email address not found.")

        if email_address.verified:
            raise serializers.ValidationError("Email address is already verified.")

        self.context["email_address"] = email_address
        return value
