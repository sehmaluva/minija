"""OTP generation, validation, and rate-limiting service."""

import secrets
import uuid
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Settings with sensible defaults
OTP_LENGTH = getattr(settings, "OTP_LENGTH", 6)
OTP_EXPIRY_MINUTES = getattr(settings, "OTP_EXPIRY_MINUTES", 10)
OTP_MAX_ATTEMPTS = getattr(settings, "OTP_MAX_ATTEMPTS", 5)
OTP_RESEND_COOLDOWN_SECONDS = getattr(settings, "OTP_RESEND_COOLDOWN_SECONDS", 60)


def generate_otp(length=None):
    """Generate a cryptographically secure numeric OTP code."""
    length = length or OTP_LENGTH
    upper = 10**length
    code = str(secrets.randbelow(upper)).zfill(length)
    return code


def create_otp(user):
    """
    Generate a new OTP code and link token, store them on the user, and return both.
    Does NOT send any email – the caller decides delivery.
    """
    code = generate_otp()
    token = uuid.uuid4()

    user.email_verification_code = code
    user.email_verification_token = token
    user.verification_code_expires_at = timezone.now() + timedelta(
        minutes=OTP_EXPIRY_MINUTES
    )
    user.verification_attempts = 0
    user.last_otp_sent_at = timezone.now()
    user.save(
        update_fields=[
            "email_verification_code",
            "email_verification_token",
            "verification_code_expires_at",
            "verification_attempts",
            "last_otp_sent_at",
        ]
    )
    logger.info("OTP created for user id=%s", user.pk)
    return code, str(token)


def create_and_send_otp(user, request=None):
    """Generate OTP, store it, and send verification email."""
    from apps.users.services.email_service import send_verification_email

    code, token = create_otp(user)
    send_verification_email(user, code, token, request)
    return code, token


def can_resend_otp(user):
    """Return True if enough time has passed since the last OTP was sent."""
    if not user.last_otp_sent_at:
        return True
    elapsed = (timezone.now() - user.last_otp_sent_at).total_seconds()
    return elapsed >= OTP_RESEND_COOLDOWN_SECONDS


def verify_otp(user, code):
    """
    Verify a 6-digit OTP code.
    Returns (success: bool, error_message: str | None).
    """
    if user.is_email_verified:
        return True, None

    if user.verification_attempts >= OTP_MAX_ATTEMPTS:
        logger.warning("OTP max attempts exceeded for user id=%s", user.pk)
        return False, "Too many attempts. Please request a new code."

    if not user.email_verification_code:
        return False, "No verification code found. Please request a new one."

    if (
        user.verification_code_expires_at
        and timezone.now() > user.verification_code_expires_at
    ):
        return False, "Verification code has expired. Please request a new one."

    user.verification_attempts += 1
    user.save(update_fields=["verification_attempts"])

    if user.email_verification_code != code:
        remaining = OTP_MAX_ATTEMPTS - user.verification_attempts
        return False, f"Invalid code. {remaining} attempt(s) remaining."

    # Success – activate the user
    _mark_verified(user)
    logger.info("OTP verified for user id=%s", user.pk)
    return True, None


def verify_token(user, token):
    """
    Verify a UUID link token (no expiry check for link tokens – they're single-use).
    Returns (success: bool, error_message: str | None).
    """
    if user.is_email_verified:
        return True, None

    if not user.email_verification_token:
        return False, "No verification token found. Please request a new one."

    if str(user.email_verification_token) != str(token):
        return False, "Invalid verification token."

    _mark_verified(user)
    logger.info("Token verified for user id=%s", user.pk)
    return True, None


def _mark_verified(user):
    """Mark user as verified and clear OTP fields."""
    user.is_email_verified = True
    user.is_active = True
    user.email_verification_code = None
    user.email_verification_token = None
    user.verification_code_expires_at = None
    user.verification_attempts = 0
    user.save(
        update_fields=[
            "is_email_verified",
            "is_active",
            "email_verification_code",
            "email_verification_token",
            "verification_code_expires_at",
            "verification_attempts",
        ]
    )
