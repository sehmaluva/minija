from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from apps.users.models.models import User


def send_verification_email(user, request):
    """
    Sends a verification email to the user with a link and a code.
    """
    token = user.email_verification_token
    # The base URL of your frontend application
    frontend_url = "http://localhost:3000/verify-email"
    verification_link = f"{frontend_url}?token={token}"

    # Generate a simple 6-digit code from the token for display
    verification_code = str(user.email_verification_token).replace("-", "")[:6].upper()

    subject = "Verify Your Account for Minija"
    # For a real project, you would use an HTML template
    message = f"""
    Hi {user.username},

    Thank you for registering. Please verify your email address to activate your account.

    You can either click the link below or use the 6-digit code in your app.

    Verification Link: {verification_link}
    Verification Code: {verification_code}

    Thanks,
    The Minija Team
    """

    send_mail(subject, message, "noreply@minija.com", [user.email])


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "password_confirm",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        # Create the user but set them as inactive until verified
        user = User.objects.create_user(
            **validated_data, is_active=False, is_email_verified=False
        )

        # Send the verification email
        send_verification_email(user, self.context.get("request"))

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")

            # Check if the user's email is verified
            if not user.is_email_verified:
                raise serializers.ValidationError(
                    "Email not verified. Please check your inbox."
                )

            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            attrs["user"] = user
        else:
            raise serializers.ValidationError("Must include email and password")

        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "role",
            "is_active",
            "last_login",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "last_login")


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number")


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
