"""Tests for permission classes."""

from unittest.mock import Mock

from django.test import TestCase

from apps.users.permissions import (
    IsOwnerOrManager,
    IsAdminOrOwner,
    CanManageBatches,
    CanViewReports,
    IsOrganizationMember,
    IsOrganizationAdmin,
    IsOrganizationOwner,
)
from apps.users.tests.factories import create_user, create_organization, add_member


def _make_request(user=None, organization=None):
    """Build a minimal mock request."""
    request = Mock()
    request.user = user or Mock(is_authenticated=False)
    request.organization = organization
    return request


# =========================================================================
# Legacy role-based permissions
# =========================================================================


class IsOwnerOrManagerTests(TestCase):
    def setUp(self):
        self.perm = IsOwnerOrManager()

    def test_unauthenticated(self):
        req = _make_request()
        self.assertFalse(self.perm.has_permission(req, None))

    def test_role_user(self):
        user = create_user(email="u@test.com", username="u")
        user.role = "user"
        user.save()
        req = _make_request(user)
        self.assertTrue(self.perm.has_permission(req, None))

    def test_role_admin(self):
        user = create_user(email="a@test.com", username="a")
        user.role = "admin"
        user.save()
        req = _make_request(user)
        self.assertTrue(self.perm.has_permission(req, None))

    def test_role_viewer_denied(self):
        user = create_user(email="v@test.com", username="v")
        user.role = "viewer"
        user.save()
        req = _make_request(user)
        self.assertFalse(self.perm.has_permission(req, None))


class IsAdminOrOwnerTests(TestCase):
    def setUp(self):
        self.perm = IsAdminOrOwner()

    def test_admin_allowed(self):
        user = create_user(email="a2@test.com", username="a2")
        user.role = "admin"
        user.save()
        req = _make_request(user)
        self.assertTrue(self.perm.has_permission(req, None))


class CanManageBatchesTests(TestCase):
    def test_user_allowed(self):
        user = create_user(email="b@test.com", username="b")
        user.role = "user"
        user.save()
        req = _make_request(user)
        self.assertTrue(CanManageBatches().has_permission(req, None))


class CanViewReportsTests(TestCase):
    def test_admin_allowed(self):
        user = create_user(email="r@test.com", username="r")
        user.role = "admin"
        user.save()
        req = _make_request(user)
        self.assertTrue(CanViewReports().has_permission(req, None))


# =========================================================================
# Organization-scoped permissions
# =========================================================================


class IsOrganizationMemberTests(TestCase):
    def setUp(self):
        self.perm = IsOrganizationMember()
        self.owner = create_user(email="owner@test.com", username="owner")
        self.org = create_organization(self.owner)

    def test_member_allowed(self):
        req = _make_request(self.owner, self.org)
        self.assertTrue(self.perm.has_permission(req, None))

    def test_non_member_denied(self):
        outsider = create_user(email="outsider@test.com", username="outsider")
        req = _make_request(outsider, self.org)
        self.assertFalse(self.perm.has_permission(req, None))

    def test_no_organization_denied(self):
        req = _make_request(self.owner, None)
        self.assertFalse(self.perm.has_permission(req, None))


class IsOrganizationAdminTests(TestCase):
    def setUp(self):
        self.perm = IsOrganizationAdmin()
        self.owner = create_user(email="owner@test.com", username="owner")
        self.admin = create_user(email="admin@test.com", username="admin_user")
        self.worker = create_user(email="worker@test.com", username="worker")
        self.org = create_organization(self.owner)
        add_member(self.org, self.admin, role="admin")
        add_member(self.org, self.worker, role="worker")

    def test_owner_allowed(self):
        req = _make_request(self.owner, self.org)
        self.assertTrue(self.perm.has_permission(req, None))

    def test_admin_allowed(self):
        req = _make_request(self.admin, self.org)
        self.assertTrue(self.perm.has_permission(req, None))

    def test_worker_denied(self):
        req = _make_request(self.worker, self.org)
        self.assertFalse(self.perm.has_permission(req, None))

    def test_object_permission_on_org(self):
        req = _make_request(self.owner)
        self.assertTrue(self.perm.has_object_permission(req, None, self.org))

    def test_object_permission_on_related_obj(self):
        """Object that has an .organization attribute."""
        obj = Mock(organization=self.org)
        req = _make_request(self.owner)
        self.assertTrue(self.perm.has_object_permission(req, None, obj))

    def test_object_permission_denied_for_worker(self):
        req = _make_request(self.worker)
        self.assertFalse(self.perm.has_object_permission(req, None, self.org))


class IsOrganizationOwnerTests(TestCase):
    def setUp(self):
        self.perm = IsOrganizationOwner()
        self.owner = create_user(email="owner@test.com", username="owner")
        self.admin = create_user(email="admin@test.com", username="admin_user")
        self.org = create_organization(self.owner)
        add_member(self.org, self.admin, role="admin")

    def test_owner_allowed(self):
        req = _make_request(self.owner, self.org)
        self.assertTrue(self.perm.has_permission(req, None))

    def test_admin_denied(self):
        req = _make_request(self.admin, self.org)
        self.assertFalse(self.perm.has_permission(req, None))

    def test_object_permission_owner_allowed(self):
        req = _make_request(self.owner)
        self.assertTrue(self.perm.has_object_permission(req, None, self.org))

    def test_object_permission_admin_denied(self):
        req = _make_request(self.admin)
        self.assertFalse(self.perm.has_object_permission(req, None, self.org))

    def test_no_organization_falls_through(self):
        """When no org on request, has_permission returns True (defers to object-level)."""
        req = _make_request(self.owner, None)
        self.assertTrue(self.perm.has_permission(req, None))
