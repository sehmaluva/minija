"""Email delivery helpers for verification and invitations."""

import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

FRONTEND_URL = getattr(settings, "FRONTEND_URL")
FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL")


def send_verification_email(user, otp_code, token, request=None):
    """
    Send a verification email containing both the 6-digit code and a clickable link.
    """
    verification_link = f"{FRONTEND_URL}/verify-email?token={token}"

    context = {
        "user": user,
        "otp_code": otp_code,
        "verification_link": verification_link,
    }

    # Try to use HTML template; fall back to plain text
    try:
        html_message = render_to_string("emails/verification_email.html", context)
        plain_message = strip_tags(html_message)
    except Exception:
        plain_message = (
            f"Hi {user.first_name or user.username},\n\n"
            f"Thank you for registering with Minija.\n\n"
            f"Your verification code is: {otp_code}\n\n"
            f"Or click this link to verify: {verification_link}\n\n"
            f"This code expires in {getattr(settings, 'OTP_EXPIRY_MINUTES', 10)} minutes.\n\n"
            f"Thanks,\nThe Minija Team"
        )
        html_message = None

    send_mail(
        subject="Verify Your Minija Account",
        message=plain_message,
        from_email=FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
    logger.info("Verification email sent to %s", user.email)


def send_invitation_email(invitation):
    """
    Send an organization invitation email.
    """
    accept_link = f"{FRONTEND_URL}/invitations/{invitation.token}/accept"

    context = {
        "invitation": invitation,
        "accept_link": accept_link,
        "organization": invitation.organization,
        "invited_by": invitation.invited_by,
    }

    try:
        html_message = render_to_string("emails/invitation_email.html", context)
        plain_message = strip_tags(html_message)
    except Exception:
        plain_message = (
            f"Hi,\n\n"
            f'You have been invited to join "{invitation.organization.name}" '
            f"as a {invitation.role} by {invitation.invited_by.full_name}.\n\n"
            f"Click this link to accept: {accept_link}\n\n"
            f"This invitation expires on {invitation.expires_at.strftime('%Y-%m-%d')}.\n\n"
            f"Thanks,\nThe Minija Team"
        )
        html_message = None

    send_mail(
        subject=f"Invitation to join {invitation.organization.name} on Minija",
        message=plain_message,
        from_email=FROM_EMAIL,
        recipient_list=[invitation.email],
        html_message=html_message,
        fail_silently=False,
    )
    logger.info(
        "Invitation email sent to %s for org=%s",
        invitation.email,
        invitation.organization.name,
    )


def send_password_reset_email(user):
    """
    Generate a password reset token, save it to the user, and send a reset email.
    """
    token = uuid.uuid4()
    user.password_reset_token = token
    user.password_reset_expires_at = timezone.now() + timedelta(hours=1)
    user.save(update_fields=["password_reset_token", "password_reset_expires_at"])

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    context = {
        "user": user,
        "reset_link": reset_link,
    }

    try:
        html_message = render_to_string("emails/password_reset_email.html", context)
        plain_message = strip_tags(html_message)
    except Exception:
        plain_message = (
            f"Hi {user.first_name or user.username},\n\n"
            f"You requested a password reset for your Minija account.\n\n"
            f"Click this link to reset your password: {reset_link}\n\n"
            f"This link expires in 1 hour.\n\n"
            f"If you didn't request this, please ignore this email.\n\n"
            f"Thanks,\nThe Minija Team"
        )
        html_message = None

    send_mail(
        subject="Reset Your Minija Password",
        message=plain_message,
        from_email=FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
    logger.info("Password reset email sent to %s", user.email)
