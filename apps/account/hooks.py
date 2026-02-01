"""Hookset for Account Management - DRF Compatible"""

import hashlib
import random

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from apps.account.conf import settings


class AccountDefaultHookSet:
    """
    Default hookset for account app.
    DRF-compatible implementation.
    """

    # ==================== EMAIL SENDING HOOKS ====================

    @staticmethod
    def send_invitation_email(to, ctx):
        """
        Send signup code invitation email.

        Args:
            to (list): List of email addresses
            ctx (dict): Context with 'signup_code', 'current_site', etc.
        """
        current_site = ctx.get("current_site")
        site_name = current_site.name if current_site else "Our Platform"
        site_domain = current_site.domain if current_site else ""
        protocol = ctx.get("protocol", "https")

        signup_code = ctx.get("signup_code")
        subject = f"You've been invited to {site_name}"

        message = f"""
Hi,

You've been invited to join {site_name}!

Your invitation code: {signup_code.code if signup_code else 'N/A'}

Register at: {protocol}://{site_domain}/register/

This code expires on: {signup_code.expiry if signup_code and signup_code.expiry else 'Never'}

Best regards,
The {site_name} Team
        """

        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, to, fail_silently=False
        )

    @staticmethod
    def send_confirmation_email(to, ctx):
        """
        Send email verification email.

        Args:
            to (list): List of email addresses
            ctx (dict): Context with 'email_address', 'key', 'activate_url'
        """
        current_site = ctx.get("current_site")
        site_name = current_site.name if current_site else "Our Platform"

        activate_url = ctx.get("activate_url", "")
        key = ctx.get("key", "")

        subject = f"Verify your email address for {site_name}"

        message = f"""
Hi,

Thanks for signing up for {site_name}!

Please verify your email address by clicking the link below or using the confirmation code.

Verification Link: {activate_url}

Verification Code: {key}

If you didn't create an account, you can safely ignore this email.

Best regards,
The {site_name} Team
        """

        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, to, fail_silently=False
        )

    @staticmethod
    def send_password_change_email(to, ctx):
        """
        Send password changed notification.

        Args:
            to (list): List of email addresses
            ctx (dict): Context with 'user', 'current_site'
        """
        user = ctx.get("user")
        current_site = ctx.get("current_site")
        site_name = current_site.name if current_site else "Our Platform"

        subject = f"Your {site_name} password has been changed"

        message = f"""
Hi {user.username if user else 'there'},

Your password for {site_name} has been successfully changed.

If you didn't make this change, please contact us immediately.

Best regards,
The {site_name} Team
        """

        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, to, fail_silently=False
        )

    @staticmethod
    def send_password_reset_email(to, ctx):
        """
        Send password reset email with token.

        Args:
            to (list): List of email addresses
            ctx (dict): Context with 'user', 'password_reset_url', 'uid', 'token'
        """
        user = ctx.get("user")
        current_site = ctx.get("current_site")
        site_name = current_site.name if current_site else "Our Platform"
        reset_url = ctx.get("password_reset_url", "")

        subject = f"Password reset for {site_name}"

        message = f"""
Hi {user.username if user else 'there'},

You requested a password reset for your {site_name} account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this, you can safely ignore this email.

Best regards,
The {site_name} Team
        """

        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, to, fail_silently=False
        )

    # ==================== TOKEN GENERATION HOOKS ====================

    @staticmethod
    def generate_random_token(extra=None, hash_func=hashlib.sha256):
        """
        Generate a random token using SHA256.

        Args:
            extra (list): Additional data to include in hash
            hash_func: Hash function to use (default: SHA256)

        Returns:
            str: Hexadecimal token string
        """
        if extra is None:
            extra = []
        bits = extra + [str(random.SystemRandom().getrandbits(512))]
        return hash_func("".join(bits).encode("utf-8")).hexdigest()

    def generate_signup_code_token(self, email=None):
        """
        Generate token for signup invitation code.

        Args:
            email (str): Optional email to include in token generation

        Returns:
            str: Generated token
        """
        extra = []
        if email:
            extra.append(email)
        return self.generate_random_token(extra)

    def generate_email_confirmation_token(self, email):
        """
        Generate token for email confirmation.

        Args:
            email (str): Email address to include in token

        Returns:
            str: Generated confirmation token
        """
        return self.generate_random_token([email])

    # ==================== AUTHENTICATION HOOKS ====================

    @staticmethod
    def get_user_credentials(form_or_data, identifier_field):
        """
        Build credentials dict for authentication.
        Works with both Django forms and DRF serializers.

        Args:
            form_or_data: Django Form or dict with cleaned_data
            identifier_field (str): Field name for username/email

        Returns:
            dict: Credentials for authenticate()
        """
        # Support both Django forms and plain dicts (from DRF serializers)
        if hasattr(form_or_data, "cleaned_data"):
            # Django Form
            data = form_or_data.cleaned_data
        elif isinstance(form_or_data, dict):
            # Plain dict (from DRF)
            data = form_or_data.get("cleaned_data", form_or_data)
        else:
            data = form_or_data

        return {
            "username": data.get(identifier_field),
            "password": data.get("password"),
        }

    # ==================== PASSWORD VALIDATION HOOKS ====================

    @staticmethod
    def clean_password(password_new, password_new_confirm):
        """
        Validate password confirmation match.
        Raises Django ValidationError (compatible with DRF).

        Args:
            password_new (str): New password
            password_new_confirm (str): Password confirmation

        Returns:
            str: The validated password

        Raises:
            ValidationError: If passwords don't match
        """
        if password_new != password_new_confirm:
            raise ValidationError(_("You must type the same password each time."))
        return password_new

    # ==================== ACCOUNT DELETION HOOKS ====================

    @staticmethod
    def account_delete_mark(deletion):
        """
        Mark account for deletion (soft delete).
        Called when user requests account deletion.

        Args:
            deletion: AccountDeletion instance
        """
        deletion.user.is_active = False
        deletion.user.save()

    @staticmethod
    def account_delete_expunge(deletion):
        """
        Permanently delete account after expunge period.
        Called by management command after delay.

        Args:
            deletion: AccountDeletion instance
        """
        deletion.user.delete()


class HookProxy:
    """
    Proxy that routes to configured hookset.
    Allows dynamic hookset configuration via settings.
    """

    def __getattr__(self, attr):
        """
        Dynamically get hookset method.
        Supports both class instances and string paths.
        """
        hookset_class = settings.ACCOUNT_HOOKSET

        # If string path, import and instantiate
        if isinstance(hookset_class, str):
            from django.utils.module_loading import import_string

            hookset_class = import_string(hookset_class)()

        return getattr(hookset_class, attr)


# Global hookset instance
hookset = HookProxy()
