"""Tests for OrganizationMiddleware."""

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from apps.users.middleware import OrganizationMiddleware
from apps.users.tests.factories import (
    create_user,
    create_organization,
    add_member,
)


def _get_response(request):
    """Dummy get_response for middleware."""
    return request


class OrganizationMiddlewareTests(TestCase):
    def setUp(self):
        self.middleware = OrganizationMiddleware(_get_response)
        self.factory = RequestFactory()
        self.owner = create_user(email="owner@test.com", username="owner")
        self.org = create_organization(self.owner, "MW Org")
        self.worker = create_user(email="worker@test.com", username="worker")
        add_member(self.org, self.worker, role="worker")

    def test_unauthenticated_user_gets_none(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        result = self.middleware(request)
        self.assertIsNone(result.organization)
        self.assertIsNone(result.organization_role)

    def test_auto_selects_first_org(self):
        """Without X-Organization-ID header, middleware picks the first org."""
        request = self.factory.get("/")
        request.user = self.owner
        result = self.middleware(request)
        self.assertEqual(result.organization, self.org)
        self.assertEqual(result.organization_role, "owner")

    def test_explicit_header_sets_org(self):
        request = self.factory.get("/", HTTP_X_ORGANIZATION_ID=str(self.org.pk))
        request.user = self.worker
        result = self.middleware(request)
        self.assertEqual(result.organization, self.org)
        self.assertEqual(result.organization_role, "worker")

    def test_invalid_org_id_returns_none(self):
        request = self.factory.get("/", HTTP_X_ORGANIZATION_ID="99999")
        request.user = self.owner
        result = self.middleware(request)
        self.assertIsNone(result.organization)
        self.assertIsNone(result.organization_role)

    def test_inactive_org_not_selected(self):
        self.org.is_active = False
        self.org.save()
        request = self.factory.get("/", HTTP_X_ORGANIZATION_ID=str(self.org.pk))
        request.user = self.owner
        result = self.middleware(request)
        self.assertIsNone(result.organization)

    def test_user_with_no_orgs_gets_none(self):
        lonely = create_user(email="lonely@test.com", username="lonely")
        request = self.factory.get("/")
        request.user = lonely
        result = self.middleware(request)
        self.assertIsNone(result.organization)
        self.assertIsNone(result.organization_role)

    def test_multiple_orgs_selects_first(self):
        """With multiple memberships, auto-select returns one (deterministic)."""
        org2 = create_organization(self.owner, "Second Org", slug="second-org")
        request = self.factory.get("/")
        request.user = self.owner
        result = self.middleware(request)
        self.assertIsNotNone(result.organization)
        self.assertIn(result.organization, [self.org, org2])
