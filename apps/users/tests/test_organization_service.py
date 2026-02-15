"""Tests for the organization service layer."""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.users.models.organization import (
    Organization,
    OrganizationMembership,
    OrganizationInvitation,
)
from apps.users.services.organization_service import (
    create_organization,
    create_default_organization,
    invite_member,
    accept_invitation,
    remove_member,
    transfer_ownership,
    _unique_slug,
)
from apps.users.tests.factories import (
    create_user,
    create_organization as factory_create_org,
    add_member,
    create_invitation,
)


# =========================================================================
# create_organization
# =========================================================================


class CreateOrganizationTests(TestCase):

    def setUp(self):
        self.user = create_user()

    def test_creates_org(self):
        org = create_organization(self.user, "My Farm")
        self.assertEqual(org.name, "My Farm")
        self.assertEqual(org.owner, self.user)
        self.assertTrue(org.is_active)

    def test_slug_auto_generated(self):
        org = create_organization(self.user, "My Farm")
        self.assertEqual(org.slug, "my-farm")

    def test_owner_membership_created(self):
        org = create_organization(self.user, "My Farm")
        m = OrganizationMembership.objects.get(organization=org, user=self.user)
        self.assertEqual(m.role, "owner")
        self.assertTrue(m.is_active)

    def test_slug_uniqueness(self):
        create_organization(self.user, "Alpha Org")
        user2 = create_user(email="u2@test.com", username="u2")
        org2 = create_organization(user2, "Alpha Org")
        self.assertNotEqual(org2.slug, "alpha-org")
        self.assertTrue(org2.slug.startswith("alpha-org"))


class CreateDefaultOrganizationTests(TestCase):

    def test_creates_with_user_name(self):
        user = create_user(first_name="Alice")
        org = create_default_organization(user)
        self.assertIn("Alice", org.name)
        self.assertEqual(org.owner, user)

    def test_uses_username_when_no_first_name(self):
        user = create_user(first_name="", username="bob99")
        org = create_default_organization(user)
        self.assertIn("bob99", org.name)


# =========================================================================
# invite_member
# =========================================================================


class InviteMemberTests(TestCase):

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.org = factory_create_org(self.owner)

    @patch("apps.users.services.organization_service.send_invitation_email")
    def test_creates_invitation(self, mock_email):
        invitation, error = invite_member(
            self.org, "new@test.com", "worker", self.owner
        )
        self.assertIsNone(error)
        self.assertIsNotNone(invitation)
        self.assertEqual(invitation.email, "new@test.com")
        self.assertEqual(invitation.role, "worker")
        self.assertEqual(invitation.status, "pending")

    @patch("apps.users.services.organization_service.send_invitation_email")
    def test_sends_email(self, mock_email):
        invite_member(self.org, "new@test.com", "worker", self.owner)
        mock_email.assert_called_once()

    @patch("apps.users.services.organization_service.send_invitation_email")
    def test_revokes_previous_pending_invitations(self, mock_email):
        inv1, _ = invite_member(self.org, "repeat@test.com", "worker", self.owner)
        inv2, _ = invite_member(self.org, "repeat@test.com", "admin", self.owner)
        inv1.refresh_from_db()
        self.assertEqual(inv1.status, "revoked")
        self.assertEqual(inv2.status, "pending")

    @patch("apps.users.services.organization_service.send_invitation_email")
    def test_rejects_existing_member(self, mock_email):
        existing = create_user(email="existing@test.com", username="existing")
        add_member(self.org, existing, role="worker")
        invitation, error = invite_member(
            self.org, "existing@test.com", "admin", self.owner
        )
        self.assertIsNone(invitation)
        self.assertIn("already a member", error)

    @override_settings(ORGANIZATION_MEMBER_LIMIT=1)
    @patch("apps.users.services.organization_service.send_invitation_email")
    def test_rejects_when_member_limit_reached(self, mock_email):
        # org already has 1 member (owner)
        invitation, error = invite_member(
            self.org, "new@test.com", "worker", self.owner
        )
        self.assertIsNone(invitation)
        self.assertIn("member limit", error)


# =========================================================================
# accept_invitation
# =========================================================================


class AcceptInvitationTests(TestCase):

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.invitee = create_user(email="invitee@test.com", username="invitee")
        self.org = factory_create_org(self.owner)
        self.invitation = create_invitation(self.org, "invitee@test.com", role="worker")

    def test_accept_success(self):
        membership, error = accept_invitation(self.invitation.token, self.invitee)
        self.assertIsNone(error)
        self.assertIsNotNone(membership)
        self.assertEqual(membership.role, "worker")
        self.assertTrue(membership.is_active)

    def test_invitation_marked_accepted(self):
        accept_invitation(self.invitation.token, self.invitee)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, "accepted")
        self.assertIsNotNone(self.invitation.accepted_at)

    def test_creates_membership(self):
        accept_invitation(self.invitation.token, self.invitee)
        self.assertTrue(
            OrganizationMembership.objects.filter(
                organization=self.org, user=self.invitee, is_active=True
            ).exists()
        )

    def test_invalid_token(self):
        import uuid

        membership, error = accept_invitation(uuid.uuid4(), self.invitee)
        self.assertIsNone(membership)
        self.assertIn("not found", error)

    def test_expired_invitation(self):
        self.invitation.expires_at = timezone.now() - timedelta(hours=1)
        self.invitation.save()
        membership, error = accept_invitation(self.invitation.token, self.invitee)
        self.assertIsNone(membership)
        self.assertIn("expired", error)

    def test_wrong_email(self):
        wrong_user = create_user(email="wrong@test.com", username="wrong")
        membership, error = accept_invitation(self.invitation.token, wrong_user)
        self.assertIsNone(membership)
        self.assertIn("different email", error)

    def test_reactivates_inactive_membership(self):
        # Create inactive membership first
        m = OrganizationMembership.objects.create(
            organization=self.org, user=self.invitee, role="admin", is_active=False
        )
        membership, error = accept_invitation(self.invitation.token, self.invitee)
        self.assertIsNone(error)
        m.refresh_from_db()
        self.assertTrue(m.is_active)
        self.assertEqual(m.role, "worker")  # updated to invitation role


# =========================================================================
# remove_member
# =========================================================================


class RemoveMemberTests(TestCase):

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.worker = create_user(email="worker@test.com", username="worker")
        self.org = factory_create_org(self.owner)
        add_member(self.org, self.worker, role="worker")

    def test_remove_member_success(self):
        success, error = remove_member(self.org, self.worker, self.owner)
        self.assertTrue(success)
        self.assertIsNone(error)
        m = OrganizationMembership.objects.get(organization=self.org, user=self.worker)
        self.assertFalse(m.is_active)

    def test_cannot_remove_owner(self):
        success, error = remove_member(self.org, self.owner, self.owner)
        self.assertFalse(success)
        self.assertIn("Cannot remove the organization owner", error)

    def test_remove_non_member(self):
        outsider = create_user(email="outsider@test.com", username="outsider")
        success, error = remove_member(self.org, outsider, self.owner)
        self.assertFalse(success)
        self.assertIn("not a member", error)


# =========================================================================
# transfer_ownership
# =========================================================================


class TransferOwnershipTests(TestCase):

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.admin = create_user(email="admin@test.com", username="admin_user")
        self.org = factory_create_org(self.owner)
        add_member(self.org, self.admin, role="admin")

    def test_transfer_success(self):
        success, error = transfer_ownership(self.org, self.admin, self.owner)
        self.assertTrue(success)
        self.assertIsNone(error)
        self.org.refresh_from_db()
        self.assertEqual(self.org.owner, self.admin)

    def test_old_owner_demoted_to_admin(self):
        transfer_ownership(self.org, self.admin, self.owner)
        m = OrganizationMembership.objects.get(organization=self.org, user=self.owner)
        self.assertEqual(m.role, "admin")

    def test_new_owner_promoted(self):
        transfer_ownership(self.org, self.admin, self.owner)
        m = OrganizationMembership.objects.get(organization=self.org, user=self.admin)
        self.assertEqual(m.role, "owner")

    def test_non_owner_cannot_transfer(self):
        success, error = transfer_ownership(self.org, self.owner, self.admin)
        self.assertFalse(success)
        self.assertIn("Only the current owner", error)

    def test_transfer_to_non_member(self):
        outsider = create_user(email="out@test.com", username="outsider")
        success, error = transfer_ownership(self.org, outsider, self.owner)
        self.assertFalse(success)
        self.assertIn("must be an active member", error)


# =========================================================================
# _unique_slug
# =========================================================================


class UniqueSlugTests(TestCase):

    def test_basic_slug(self):
        self.assertEqual(_unique_slug("Happy Farm"), "happy-farm")

    def test_increments_on_conflict(self):
        owner = create_user()
        factory_create_org(owner, name="My Org", slug="my-org")
        slug = _unique_slug("My Org")
        self.assertEqual(slug, "my-org-1")
