"""Tests for email delivery service."""

from unittest.mock import patch, MagicMock
from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.users.services.email_service import (
    send_verification_email,
    send_invitation_email,
)
from apps.users.tests.factories import (
    create_user,
    create_organization,
    create_invitation,
)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    FRONTEND_URL="http://localhost:3000",
    DEFAULT_FROM_EMAIL="noreply@minija.com",
)
class SendVerificationEmailTests(TestCase):

    def setUp(self):
        self.user = create_user(email="verify@test.com", first_name="Alice")

    @patch("apps.users.services.email_service.send_mail")
    def test_sends_email_to_user(self, mock_send_mail):
        send_verification_email(self.user, "123456", "some-token-uuid")
        mock_send_mail.assert_called_once()
        kwargs = mock_send_mail.call_args
        # Check recipient
        self.assertIn(
            "verify@test.com",
            (
                kwargs[1].get("recipient_list", [])
                if len(kwargs) > 1 and isinstance(kwargs[1], dict)
                else kwargs.kwargs.get("recipient_list", [])
            ),
        )

    @patch("apps.users.services.email_service.send_mail")
    def test_subject_contains_minija(self, mock_send_mail):
        send_verification_email(self.user, "123456", "token")
        call_args = mock_send_mail.call_args
        subject = call_args.kwargs.get(
            "subject", call_args[0][0] if call_args[0] else ""
        )
        self.assertIn("Minija", subject)

    @patch(
        "apps.users.services.email_service.render_to_string",
        side_effect=Exception("no template"),
    )
    @patch("apps.users.services.email_service.send_mail")
    def test_fallback_plain_text(self, mock_send_mail, mock_render):
        send_verification_email(self.user, "654321", "token-abc")
        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args
        message = call_args.kwargs.get(
            "message", call_args[0][1] if len(call_args[0]) > 1 else ""
        )
        self.assertIn("654321", message)
        self.assertIn("token-abc", message)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    FRONTEND_URL="http://localhost:3000",
    DEFAULT_FROM_EMAIL="noreply@minija.com",
)
class SendInvitationEmailTests(TestCase):

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.org = create_organization(self.owner, name="Farmville")
        self.invitation = create_invitation(self.org, "guest@test.com", role="worker")

    @patch("apps.users.services.email_service.send_mail")
    def test_sends_email_to_invitee(self, mock_send_mail):
        send_invitation_email(self.invitation)
        mock_send_mail.assert_called_once()

    @patch(
        "apps.users.services.email_service.render_to_string",
        side_effect=Exception("no template"),
    )
    @patch("apps.users.services.email_service.send_mail")
    def test_fallback_contains_org_name(self, mock_send_mail, mock_render):
        send_invitation_email(self.invitation)
        call_args = mock_send_mail.call_args
        message = call_args.kwargs.get(
            "message", call_args[0][1] if len(call_args[0]) > 1 else ""
        )
        self.assertIn("Farmville", message)

    @patch(
        "apps.users.services.email_service.render_to_string",
        side_effect=Exception("no template"),
    )
    @patch("apps.users.services.email_service.send_mail")
    def test_fallback_contains_accept_link(self, mock_send_mail, mock_render):
        send_invitation_email(self.invitation)
        call_args = mock_send_mail.call_args
        message = call_args.kwargs.get(
            "message", call_args[0][1] if len(call_args[0]) > 1 else ""
        )
        self.assertIn(str(self.invitation.token), message)
        self.assertIn("invitations/", message)
