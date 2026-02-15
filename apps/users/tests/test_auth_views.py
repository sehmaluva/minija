"""Tests for authentication API views (register, login, verify, profile, etc.)."""

import uuid
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models.models import User
from apps.users.tests.factories import create_user


def get_auth_client(user):
    """Return an APIClient authenticated with JWT for *user*."""
    from rest_framework_simplejwt.tokens import RefreshToken

    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


# =========================================================================
# Registration
# =========================================================================


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegisterViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("register")
        self.valid_data = {
            "email": "new@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }

    @patch("apps.users.services.email_service.send_mail")
    def test_register_success(self, mock_mail):
        resp = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)
        self.assertIn("user", resp.data)

    @patch("apps.users.services.email_service.send_mail")
    def test_register_creates_user(self, mock_mail):
        self.client.post(self.url, self.valid_data, format="json")
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    @patch("apps.users.services.email_service.send_mail")
    def test_register_user_inactive_and_unverified(self, mock_mail):
        self.client.post(self.url, self.valid_data, format="json")
        user = User.objects.get(email="new@example.com")
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_email_verified)

    @patch("apps.users.services.email_service.send_mail")
    def test_register_creates_default_organization(self, mock_mail):
        self.client.post(self.url, self.valid_data, format="json")
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.get_organizations().count(), 1)

    @patch("apps.users.services.email_service.send_mail")
    def test_register_sends_verification_email(self, mock_mail):
        self.client.post(self.url, self.valid_data, format="json")
        mock_mail.assert_called_once()

    def test_register_password_mismatch(self):
        data = {**self.valid_data, "password_confirm": "Different123!"}
        resp = self.client.post(self.url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.users.services.email_service.send_mail")
    def test_register_duplicate_email(self, mock_mail):
        create_user(email="new@example.com", username="existing")
        resp = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        data = {**self.valid_data, "password": "123", "password_confirm": "123"}
        resp = self.client.post(self.url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        resp = self.client.post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


# =========================================================================
# Email Verification
# =========================================================================


class EmailVerificationViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("email_verify")
        self.token = uuid.uuid4()
        self.user = create_user(
            is_active=False,
            is_email_verified=False,
            email_verification_token=self.token,
        )
        self.user.email_verification_code = "123456"
        self.user.verification_code_expires_at = timezone.now() + timedelta(minutes=10)
        self.user.save()

    # --- GET (link-based) ---

    def test_verify_link_success(self):
        resp = self.client.get(self.url, {"token": str(self.token)})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_verify_link_invalid_token(self):
        resp = self.client.get(self.url, {"token": str(uuid.uuid4())})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_link_missing_token(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Token is required", resp.data["error"])

    # --- POST (code-based) ---

    def test_verify_code_success(self):
        resp = self.client.post(
            self.url,
            {"email": self.user.email, "code": "123456"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_verify_code_wrong(self):
        resp = self.client.post(
            self.url,
            {"email": self.user.email, "code": "000000"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_code_missing_fields(self):
        resp = self.client.post(self.url, {"email": self.user.email}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_code_nonexistent_email(self):
        resp = self.client.post(
            self.url,
            {"email": "nope@test.com", "code": "123456"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


# =========================================================================
# Resend Verification
# =========================================================================


class ResendVerificationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("resend_verification")
        self.user = create_user(
            is_email_verified=False,
            email_verification_token=uuid.uuid4(),
        )

    @patch("apps.users.services.email_service.send_mail")
    def test_resend_success(self, mock_mail):
        resp = self.client.post(self.url, {"email": self.user.email}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_resend_missing_email(self):
        resp = self.client.post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resend_nonexistent_email_no_info_leak(self):
        resp = self.client.post(self.url, {"email": "nope@test.com"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("If an account", resp.data["message"])

    def test_resend_already_verified(self):
        self.user.is_email_verified = True
        self.user.save()
        resp = self.client.post(self.url, {"email": self.user.email}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("already been verified", resp.data["message"])

    @patch("apps.users.services.email_service.send_mail")
    def test_resend_rate_limited(self, mock_mail):
        self.user.last_otp_sent_at = timezone.now()
        self.user.save()
        resp = self.client.post(self.url, {"email": self.user.email}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


# =========================================================================
# Login
# =========================================================================


class LoginViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("login")
        self.user = create_user(
            email="login@test.com",
            username="loginuser",
            is_active=True,
            is_email_verified=True,
        )

    def test_login_success(self):
        resp = self.client.post(
            self.url,
            {"email": "login@test.com", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)
        self.assertIn("user", resp.data)

    def test_login_wrong_password(self):
        resp = self.client.post(
            self.url, {"email": "login@test.com", "password": "Wrong!"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_email(self):
        resp = self.client.post(
            self.url, {"email": "nope@test.com", "password": "Pass123!"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unverified_email(self):
        unverified = create_user(
            email="unver@test.com",
            username="unver",
            is_active=True,
            is_email_verified=False,
        )
        resp = self.client.post(
            self.url,
            {"email": "unver@test.com", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user(self):
        inactive = create_user(
            email="inactive@test.com",
            username="inactive",
            is_active=False,
            is_email_verified=True,
        )
        resp = self.client.post(
            self.url,
            {"email": "inactive@test.com", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        resp = self.client.post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


# =========================================================================
# Logout
# =========================================================================


class LogoutViewTests(TestCase):

    def setUp(self):
        self.user = create_user(email="logout@test.com", username="logoutuser")
        self.client = get_auth_client(self.user)
        self.url = reverse("logout")

    def test_logout_success(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated(self):
        client = APIClient()
        resp = client.post(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


# =========================================================================
# Profile
# =========================================================================


class ProfileViewTests(TestCase):

    def setUp(self):
        self.user = create_user(
            email="profile@test.com",
            username="profileuser",
            first_name="Original",
            last_name="Name",
        )
        self.client = get_auth_client(self.user)
        self.url = reverse("profile")

    def test_get_profile(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["email"], "profile@test.com")
        self.assertEqual(resp.data["first_name"], "Original")

    def test_update_profile(self):
        resp = self.client.patch(self.url, {"first_name": "Updated"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_update_phone_number(self):
        resp = self.client.patch(
            self.url, {"phone_number": "+1234567890"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, "+1234567890")

    def test_unauthenticated_access(self):
        resp = APIClient().get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


# =========================================================================
# Change Password
# =========================================================================


class ChangePasswordViewTests(TestCase):

    def setUp(self):
        self.user = create_user(email="pw@test.com", username="pwuser")
        self.client = get_auth_client(self.user)
        self.url = reverse("change_password")

    def test_change_password_success(self):
        resp = self.client.post(
            self.url,
            {
                "old_password": "SecurePass123!",
                "new_password": "NewSecurePass456!",
                "new_password_confirm": "NewSecurePass456!",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecurePass456!"))

    def test_change_password_wrong_old(self):
        resp = self.client.post(
            self.url,
            {
                "old_password": "WrongOld!",
                "new_password": "NewSecurePass456!",
                "new_password_confirm": "NewSecurePass456!",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        resp = self.client.post(
            self.url,
            {
                "old_password": "SecurePass123!",
                "new_password": "NewSecurePass456!",
                "new_password_confirm": "Mismatch789!",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        resp = APIClient().post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


# =========================================================================
# User List
# =========================================================================


class UserListViewTests(TestCase):

    def test_admin_sees_all_users(self):
        admin = create_user(email="admin@test.com", username="admin", role="admin")
        create_user(email="other@test.com", username="other")
        client = get_auth_client(admin)
        resp = client.get(reverse("user_list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_regular_user_sees_only_self(self):
        user = create_user(email="regular@test.com", username="regular")
        create_user(email="other@test.com", username="other")
        client = get_auth_client(user)
        resp = client.get(reverse("user_list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["email"], "regular@test.com")


# =========================================================================
# Permissions endpoint
# =========================================================================


class UserPermissionsViewTests(TestCase):

    def test_admin_permissions(self):
        admin = create_user(email="a@test.com", username="a", role="admin")
        client = get_auth_client(admin)
        resp = client.get(reverse("user_permissions"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["permissions"]["can_manage_users"])

    def test_regular_user_permissions(self):
        user = create_user(email="u@test.com", username="u", role="user")
        client = get_auth_client(user)
        resp = client.get(reverse("user_permissions"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(resp.data["permissions"]["can_manage_users"])
        self.assertTrue(resp.data["permissions"]["can_view_reports"])
