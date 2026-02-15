"""Tests for User and Organization models."""

import uuid
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.users.models.models import User
from apps.users.models.organization import (
    Organization,
    OrganizationMembership,
    OrganizationInvitation,
)
from apps.users.tests.factories import create_user, create_organization, add_member


# =========================================================================
# User model
# =========================================================================


class UserModelTests(TestCase):
    """Tests for the custom User model."""

    def test_create_user(self):
        user = create_user()
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("SecurePass123!"))
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        su = User.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="AdminPass123!",
            first_name="Admin",
            last_name="User",
        )
        self.assertTrue(su.is_superuser)
        self.assertTrue(su.is_staff)

    def test_email_is_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_required_fields(self):
        self.assertIn("username", User.REQUIRED_FIELDS)
        self.assertIn("first_name", User.REQUIRED_FIELDS)
        self.assertIn("last_name", User.REQUIRED_FIELDS)

    def test_email_unique(self):
        create_user(email="dup@example.com", username="u1")
        with self.assertRaises(Exception):
            create_user(email="dup@example.com", username="u2")

    def test_full_name_property(self):
        user = create_user(first_name="John", last_name="Doe")
        self.assertEqual(user.full_name, "John Doe")

    def test_full_name_strips_whitespace(self):
        user = create_user(first_name="", last_name="Solo")
        self.assertEqual(user.full_name, "Solo")

    def test_str_representation(self):
        user = create_user(first_name="Test", last_name="User")
        self.assertEqual(str(user), "Test User (test@example.com)")

    def test_default_role(self):
        user = create_user()
        self.assertEqual(user.role, "user")

    def test_admin_role(self):
        user = create_user(role="admin")
        self.assertEqual(user.role, "admin")

    def test_otp_fields_default_to_none(self):
        user = create_user()
        self.assertIsNone(user.email_verification_code)
        self.assertIsNone(user.verification_code_expires_at)
        self.assertEqual(user.verification_attempts, 0)
        self.assertIsNone(user.last_otp_sent_at)

    def test_timestamps_auto_set(self):
        user = create_user()
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

    def test_db_table_name(self):
        self.assertEqual(User._meta.db_table, "users")


# =========================================================================
# Organization helpers on User
# =========================================================================


class UserOrganizationHelpersTests(TestCase):
    """Tests for organization helper methods on User."""

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.admin = create_user(email="admin@test.com", username="admin_user")
        self.worker = create_user(email="worker@test.com", username="worker_user")
        self.outsider = create_user(email="outsider@test.com", username="outsider")

        self.org = create_organization(self.owner, name="Alpha Org")
        add_member(self.org, self.admin, role="admin")
        add_member(self.org, self.worker, role="worker")

    def test_get_organizations(self):
        orgs = self.owner.get_organizations()
        self.assertEqual(orgs.count(), 1)
        self.assertIn(self.org, orgs)

    def test_get_organizations_excludes_inactive_membership(self):
        membership = OrganizationMembership.objects.get(
            organization=self.org, user=self.worker
        )
        membership.is_active = False
        membership.save()
        self.assertEqual(self.worker.get_organizations().count(), 0)

    def test_get_role_in_organization(self):
        self.assertEqual(self.owner.get_role_in_organization(self.org), "owner")
        self.assertEqual(self.admin.get_role_in_organization(self.org), "admin")
        self.assertEqual(self.worker.get_role_in_organization(self.org), "worker")
        self.assertIsNone(self.outsider.get_role_in_organization(self.org))

    def test_is_owner_of(self):
        self.assertTrue(self.owner.is_owner_of(self.org))
        self.assertFalse(self.admin.is_owner_of(self.org))

    def test_is_admin_of(self):
        self.assertTrue(self.owner.is_admin_of(self.org))  # owner counts as admin
        self.assertTrue(self.admin.is_admin_of(self.org))
        self.assertFalse(self.worker.is_admin_of(self.org))

    def test_is_member_of(self):
        self.assertTrue(self.owner.is_member_of(self.org))
        self.assertTrue(self.worker.is_member_of(self.org))
        self.assertFalse(self.outsider.is_member_of(self.org))


# =========================================================================
# Organization model
# =========================================================================


class OrganizationModelTests(TestCase):
    """Tests for the Organization model."""

    def setUp(self):
        self.owner = create_user()
        self.org = create_organization(self.owner)

    def test_str_representation(self):
        self.assertEqual(str(self.org), "Test Org")

    def test_member_count_property(self):
        self.assertEqual(self.org.member_count, 1)  # owner only
        another = create_user(email="m@test.com", username="m1")
        add_member(self.org, another)
        self.assertEqual(self.org.member_count, 2)

    def test_member_count_excludes_inactive(self):
        member = create_user(email="inactive@test.com", username="inactive_m")
        membership = add_member(self.org, member)
        self.assertEqual(self.org.member_count, 2)
        membership.is_active = False
        membership.save()
        self.assertEqual(self.org.member_count, 1)

    def test_slug_unique(self):
        with self.assertRaises(Exception):
            Organization.objects.create(
                name="Another", slug=self.org.slug, owner=self.owner
            )

    def test_ordering(self):
        org2 = create_organization(self.owner, name="Second Org", slug="second-org")
        orgs = list(Organization.objects.all())
        self.assertEqual(orgs[0], org2)  # most recently created first

    def test_db_table_name(self):
        self.assertEqual(Organization._meta.db_table, "organizations")


# =========================================================================
# OrganizationMembership model
# =========================================================================


class MembershipModelTests(TestCase):
    """Tests for OrganizationMembership model."""

    def setUp(self):
        self.owner = create_user()
        self.org = create_organization(self.owner)

    def test_str_representation(self):
        m = OrganizationMembership.objects.get(organization=self.org, user=self.owner)
        self.assertIn("owner", str(m))
        self.assertIn(str(self.owner), str(m))

    def test_unique_together(self):
        """Cannot create duplicate membership for same (org, user)."""
        with self.assertRaises(Exception):
            OrganizationMembership.objects.create(
                organization=self.org, user=self.owner, role="admin"
            )

    def test_default_permissions_empty_dict(self):
        m = OrganizationMembership.objects.get(organization=self.org, user=self.owner)
        self.assertEqual(m.permissions, {})

    def test_db_table_name(self):
        self.assertEqual(
            OrganizationMembership._meta.db_table, "organization_memberships"
        )


# =========================================================================
# OrganizationInvitation model
# =========================================================================


class InvitationModelTests(TestCase):
    """Tests for OrganizationInvitation model."""

    def setUp(self):
        self.owner = create_user()
        self.org = create_organization(self.owner)

    def test_str_representation(self):
        inv = OrganizationInvitation.objects.create(
            organization=self.org,
            email="invite@test.com",
            role="worker",
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.assertIn("invite@test.com", str(inv))
        self.assertIn("pending", str(inv))

    def test_default_status_pending(self):
        inv = OrganizationInvitation.objects.create(
            organization=self.org,
            email="inv@test.com",
            role="worker",
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.assertEqual(inv.status, "pending")

    def test_token_auto_generated(self):
        inv = OrganizationInvitation.objects.create(
            organization=self.org,
            email="token@test.com",
            role="admin",
            invited_by=self.owner,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.assertIsNotNone(inv.token)
        # Must be a valid UUID
        uuid.UUID(str(inv.token))

    def test_db_table_name(self):
        self.assertEqual(
            OrganizationInvitation._meta.db_table, "organization_invitations"
        )
