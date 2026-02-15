"""Tests for OTP service (generation, verification, rate-limiting)."""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.users.services.otp_service import (
    generate_otp,
    create_otp,
    create_and_send_otp,
    can_resend_otp,
    verify_otp,
    verify_token,
    _mark_verified,
)
from apps.users.tests.factories import create_user


class GenerateOTPTests(TestCase):
    """Tests for generate_otp function."""

    def test_default_length_6(self):
        code = generate_otp()
        self.assertEqual(len(code), 6)

    def test_custom_length(self):
        code = generate_otp(length=8)
        self.assertEqual(len(code), 8)

    def test_is_numeric(self):
        code = generate_otp()
        self.assertTrue(code.isdigit())

    def test_zero_padded(self):
        """Code should be zero-padded to requested length."""
        # Run many times to increase chance of hitting a low number
        for _ in range(50):
            code = generate_otp(length=6)
            self.assertEqual(len(code), 6)


class CreateOTPTests(TestCase):
    """Tests for create_otp function."""

    def setUp(self):
        self.user = create_user(is_email_verified=False)

    def test_creates_code_and_token(self):
        code, token = create_otp(self.user)
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())
        # token is a UUID string
        self.assertEqual(len(token), 36)

    def test_stores_code_on_user(self):
        code, _ = create_otp(self.user)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email_verification_code, code)

    def test_stores_token_on_user(self):
        _, token = create_otp(self.user)
        self.user.refresh_from_db()
        self.assertEqual(str(self.user.email_verification_token), token)

    def test_sets_expiry(self):
        create_otp(self.user)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.verification_code_expires_at)
        # Should expire in ~10 minutes
        diff = self.user.verification_code_expires_at - timezone.now()
        self.assertAlmostEqual(diff.total_seconds(), 600, delta=5)

    def test_resets_attempts(self):
        self.user.verification_attempts = 3
        self.user.save()
        create_otp(self.user)
        self.user.refresh_from_db()
        self.assertEqual(self.user.verification_attempts, 0)

    def test_sets_last_otp_sent_at(self):
        create_otp(self.user)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_otp_sent_at)


class CreateAndSendOTPTests(TestCase):
    """Tests for create_and_send_otp function."""

    def setUp(self):
        self.user = create_user(is_email_verified=False)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    @patch("apps.users.services.email_service.send_mail")
    def test_sends_email(self, mock_send_mail):
        code, token = create_and_send_otp(self.user)
        mock_send_mail.assert_called_once()
        call_kwargs = mock_send_mail.call_args
        self.assertIn(
            self.user.email,
            call_kwargs.kwargs.get(
                "recipient_list", call_kwargs[1] if len(call_kwargs[1]) > 3 else []
            ),
        )

    @patch("apps.users.services.email_service.send_mail")
    def test_returns_code_and_token(self, mock_send_mail):
        code, token = create_and_send_otp(self.user)
        self.assertEqual(len(code), 6)
        self.assertEqual(len(token), 36)


class CanResendOTPTests(TestCase):
    """Tests for can_resend_otp rate-limiting."""

    def setUp(self):
        self.user = create_user(is_email_verified=False)

    def test_can_resend_when_never_sent(self):
        self.user.last_otp_sent_at = None
        self.user.save()
        self.assertTrue(can_resend_otp(self.user))

    def test_cannot_resend_too_soon(self):
        self.user.last_otp_sent_at = timezone.now()
        self.user.save()
        self.assertFalse(can_resend_otp(self.user))

    @override_settings(OTP_RESEND_COOLDOWN_SECONDS=60)
    def test_can_resend_after_cooldown(self):
        self.user.last_otp_sent_at = timezone.now() - timedelta(seconds=61)
        self.user.save()
        self.assertTrue(can_resend_otp(self.user))


class VerifyOTPTests(TestCase):
    """Tests for verify_otp function."""

    def setUp(self):
        self.user = create_user(is_email_verified=False)
        self.user.email_verification_code = "123456"
        self.user.verification_code_expires_at = timezone.now() + timedelta(minutes=10)
        self.user.verification_attempts = 0
        self.user.save()

    def test_successful_verification(self):
        success, error = verify_otp(self.user, "123456")
        self.assertTrue(success)
        self.assertIsNone(error)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_clears_otp_fields_on_success(self):
        verify_otp(self.user, "123456")
        self.user.refresh_from_db()
        self.assertIsNone(self.user.email_verification_code)
        self.assertIsNone(self.user.email_verification_token)
        self.assertIsNone(self.user.verification_code_expires_at)
        self.assertEqual(self.user.verification_attempts, 0)

    def test_wrong_code(self):
        success, error = verify_otp(self.user, "999999")
        self.assertFalse(success)
        self.assertIn("Invalid code", error)

    def test_wrong_code_increments_attempts(self):
        verify_otp(self.user, "999999")
        self.user.refresh_from_db()
        self.assertEqual(self.user.verification_attempts, 1)

    def test_expired_code(self):
        self.user.verification_code_expires_at = timezone.now() - timedelta(minutes=1)
        self.user.save()
        success, error = verify_otp(self.user, "123456")
        self.assertFalse(success)
        self.assertIn("expired", error)

    @override_settings(OTP_MAX_ATTEMPTS=5)
    def test_max_attempts_exceeded(self):
        self.user.verification_attempts = 5
        self.user.save()
        success, error = verify_otp(self.user, "123456")
        self.assertFalse(success)
        self.assertIn("Too many attempts", error)

    def test_no_code_set(self):
        self.user.email_verification_code = None
        self.user.save()
        success, error = verify_otp(self.user, "123456")
        self.assertFalse(success)
        self.assertIn("No verification code found", error)

    def test_already_verified_returns_true(self):
        self.user.is_email_verified = True
        self.user.save()
        success, error = verify_otp(self.user, "wrong")
        self.assertTrue(success)
        self.assertIsNone(error)

    def test_remaining_attempts_in_error_message(self):
        success, error = verify_otp(self.user, "999999")
        self.assertIn("4 attempt(s) remaining", error)


class VerifyTokenTests(TestCase):
    """Tests for verify_token function."""

    def setUp(self):
        import uuid

        self.token = uuid.uuid4()
        self.user = create_user(
            is_email_verified=False, email_verification_token=self.token
        )

    def test_successful_token_verification(self):
        success, error = verify_token(self.user, str(self.token))
        self.assertTrue(success)
        self.assertIsNone(error)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_invalid_token(self):
        import uuid

        success, error = verify_token(self.user, str(uuid.uuid4()))
        self.assertFalse(success)
        self.assertIn("Invalid verification token", error)

    def test_no_token_set(self):
        self.user.email_verification_token = None
        self.user.save()
        success, error = verify_token(self.user, "some-token")
        self.assertFalse(success)
        self.assertIn("No verification token found", error)

    def test_already_verified_returns_true(self):
        self.user.is_email_verified = True
        self.user.save()
        success, error = verify_token(self.user, "wrong-token")
        self.assertTrue(success)


class MarkVerifiedTests(TestCase):
    """Tests for _mark_verified helper."""

    def test_mark_verified_sets_flags(self):
        user = create_user(is_email_verified=False, is_active=False)
        user.email_verification_code = "123456"
        user.save()
        _mark_verified(user)
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)
        self.assertTrue(user.is_active)
        self.assertIsNone(user.email_verification_code)
        self.assertIsNone(user.email_verification_token)
        self.assertEqual(user.verification_attempts, 0)
