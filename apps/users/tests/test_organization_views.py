"""Tests for Organization API views."""

import uuid
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models.organization import (
    Organization,
    OrganizationMembership,
    OrganizationInvitation,
)
from apps.users.tests.factories import (
    create_user,
    create_organization,
    add_member,
    create_invitation,
)


def get_auth_client(user, org=None):
    """Return an APIClient with JWT and optional X-Organization-ID header."""
    client = APIClient()
    token = RefreshToken.for_user(user)
    headers = {"HTTP_AUTHORIZATION": f"Bearer {token.access_token}"}
    if org:
        headers["HTTP_X_ORGANIZATION_ID"] = str(org.pk)
    client.credentials(**headers)
    return client


# =========================================================================
# Organization CRUD
# =========================================================================


class OrganizationListCreateTests(TestCase):
    """Tests for GET/POST /api/organizations/."""

    def setUp(self):
        self.url = reverse("organization_list_create")
        self.user = create_user(email="org@test.com", username="orguser")
        self.client = get_auth_client(self.user)

    def test_list_empty(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 0)

    def test_list_returns_own_orgs(self):
        create_organization(self.user, "Org A")
        create_organization(self.user, "Org B", slug="org-b")

        # Another user's org — should NOT appear
        other = create_user(email="other@test.com", username="other")
        create_organization(other, "Other Org")

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    @patch("apps.users.services.organization_service.send_invitation_email")
    def test_create_organization(self, _):
        resp = self.client.post(
            self.url, {"name": "New Org", "description": "desc"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["name"], "New Org")
        self.assertTrue(Organization.objects.filter(name="New Org").exists())

    def test_create_requires_auth(self):
        resp = APIClient().post(self.url, {"name": "No Auth"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class OrganizationDetailTests(TestCase):
    """Tests for GET/PATCH/DELETE /api/organizations/<pk>/."""

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.org = create_organization(self.owner, "Detail Org")
        self.client = get_auth_client(self.owner, self.org)

    def test_retrieve(self):
        url = reverse("organization_detail", kwargs={"pk": self.org.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Detail Org")

    def test_update_name(self):
        url = reverse("organization_detail", kwargs={"pk": self.org.pk})
        resp = self.client.patch(url, {"name": "Renamed"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.org.refresh_from_db()
        self.assertEqual(self.org.name, "Renamed")

    def test_soft_delete(self):
        url = reverse("organization_detail", kwargs={"pk": self.org.pk})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.org.refresh_from_db()
        self.assertFalse(self.org.is_active)

    def test_non_member_cannot_access(self):
        outsider = create_user(email="outsider@test.com", username="outsider")
        c = get_auth_client(outsider)
        url = reverse("organization_detail", kwargs={"pk": self.org.pk})
        resp = c.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


# =========================================================================
# Members
# =========================================================================


class OrganizationMembersTests(TestCase):
    """Tests for GET /api/organizations/<pk>/members/."""

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.worker = create_user(email="worker@test.com", username="worker")
        self.org = create_organization(self.owner)
        add_member(self.org, self.worker, role="worker")
        self.client = get_auth_client(self.owner, self.org)

    def test_list_members(self):
        url = reverse("organization_members", kwargs={"pk": self.org.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)  # owner + worker


class InviteMemberTests(TestCase):
    """Tests for POST /api/organizations/<pk>/members/invite/."""

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.org = create_organization(self.owner)
        self.client = get_auth_client(self.owner, self.org)
        self.url = reverse("organization_invite_member", kwargs={"pk": self.org.pk})

    @patch("apps.users.services.organization_service.send_invitation_email")
    def test_invite_success(self, mock_email):
        resp = self.client.post(
            self.url, {"email": "new@test.com", "role": "worker"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            OrganizationInvitation.objects.filter(
                email="new@test.com", status="pending"
            ).exists()
        )

    @patch("apps.users.services.organization_service.send_invitation_email")
    def test_invite_existing_member_fails(self, mock_email):
        existing = create_user(email="member@test.com", username="member")
        add_member(self.org, existing)
        resp = self.client.post(
            self.url, {"email": "member@test.com", "role": "admin"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_worker_cannot_invite(self):
        worker = create_user(email="w@test.com", username="w")
        add_member(self.org, worker, role="worker")
        c = get_auth_client(worker, self.org)
        resp = c.post(
            self.url, {"email": "x@test.com", "role": "worker"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class UpdateMemberRoleTests(TestCase):
    """Tests for PATCH /api/organizations/<pk>/members/<user_id>/role/."""

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.admin = create_user(email="admin@test.com", username="admin_user")
        self.org = create_organization(self.owner)
        add_member(self.org, self.admin, role="admin")
        self.client = get_auth_client(self.owner, self.org)

    def test_update_role_success(self):
        url = reverse(
            "organization_update_member_role",
            kwargs={"pk": self.org.pk, "user_id": self.admin.pk},
        )
        resp = self.client.patch(url, {"role": "worker"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        m = OrganizationMembership.objects.get(organization=self.org, user=self.admin)
        self.assertEqual(m.role, "worker")

    def test_cannot_change_owner_role(self):
        url = reverse(
            "organization_update_member_role",
            kwargs={"pk": self.org.pk, "user_id": self.owner.pk},
        )
        resp = self.client.patch(url, {"role": "admin"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class RemoveMemberTests(TestCase):
    """Tests for DELETE /api/organizations/<pk>/members/<user_id>/."""

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.worker = create_user(email="worker@test.com", username="worker")
        self.org = create_organization(self.owner)
        add_member(self.org, self.worker, role="worker")
        self.client = get_auth_client(self.owner, self.org)

    def test_remove_member_success(self):
        url = reverse(
            "organization_remove_member",
            kwargs={"pk": self.org.pk, "user_id": self.worker.pk},
        )
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_cannot_remove_owner(self):
        url = reverse(
            "organization_remove_member",
            kwargs={"pk": self.org.pk, "user_id": self.owner.pk},
        )
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


# =========================================================================
# Invitations
# =========================================================================


class AcceptInvitationTests(TestCase):
    """Tests for POST /api/invitations/<token>/accept/."""

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.invitee = create_user(email="invitee@test.com", username="invitee")
        self.org = create_organization(self.owner)
        self.invitation = create_invitation(self.org, "invitee@test.com")
        self.client = get_auth_client(self.invitee)

    def test_accept_success(self):
        url = reverse("accept_invitation", kwargs={"token": str(self.invitation.token)})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("membership", resp.data)

    def test_accept_invalid_token(self):
        url = reverse("accept_invitation", kwargs={"token": str(uuid.uuid4())})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class PendingInvitationsTests(TestCase):
    """Tests for GET /api/invitations/pending/."""

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.invitee = create_user(email="invitee@test.com", username="invitee")
        self.org = create_organization(self.owner)
        create_invitation(self.org, "invitee@test.com")
        self.client = get_auth_client(self.invitee)

    def test_list_pending_invitations(self):
        url = reverse("pending_invitations")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_no_invitations_for_other_user(self):
        other = create_user(email="other@test.com", username="other")
        c = get_auth_client(other)
        url = reverse("pending_invitations")
        resp = c.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 0)


class RevokeInvitationTests(TestCase):
    """Tests for DELETE /api/invitations/<pk>/."""

    def setUp(self):
        self.owner = create_user(email="owner@test.com", username="owner")
        self.org = create_organization(self.owner)
        self.invitation = create_invitation(self.org, "guest@test.com")
        self.client = get_auth_client(self.owner, self.org)

    def test_revoke_success(self):
        url = reverse("revoke_invitation", kwargs={"pk": self.invitation.pk})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, "revoked")

    def test_revoke_nonexistent(self):
        url = reverse("revoke_invitation", kwargs={"pk": 99999})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
