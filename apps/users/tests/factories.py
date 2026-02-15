"""Shared test helpers and factories for the users app."""

from django.utils import timezone
from apps.users.models.models import User
from apps.users.models.organization import (
    Organization,
    OrganizationMembership,
    OrganizationInvitation,
)


def create_user(
    email="test@example.com",
    username="testuser",
    password="SecurePass123!",
    first_name="Test",
    last_name="User",
    is_active=True,
    is_email_verified=True,
    role="user",
    **kwargs,
):
    """Create and return a test user."""
    return User.objects.create_user(
        email=email,
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=is_active,
        is_email_verified=is_email_verified,
        role=role,
        **kwargs,
    )


def create_organization(owner, name="Test Org", description="", slug=None):
    """Create an organization with owner membership."""
    from django.utils.text import slugify

    slug = slug or slugify(name)
    org = Organization.objects.create(
        name=name,
        slug=slug,
        description=description,
        owner=owner,
    )
    OrganizationMembership.objects.create(
        organization=org,
        user=owner,
        role="owner",
    )
    return org


def add_member(organization, user, role="worker"):
    """Add a user to an organization."""
    return OrganizationMembership.objects.create(
        organization=organization,
        user=user,
        role=role,
    )


def create_invitation(organization, email, role="worker", invited_by=None, **kwargs):
    """Create an organization invitation."""
    import uuid
    from datetime import timedelta

    defaults = {
        "organization": organization,
        "email": email,
        "role": role,
        "invited_by": invited_by or organization.owner,
        "expires_at": timezone.now() + timedelta(days=7),
    }
    defaults.update(kwargs)
    return OrganizationInvitation.objects.create(**defaults)
