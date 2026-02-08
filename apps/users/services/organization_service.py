"""Business logic for organization lifecycle management."""

import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)

INVITATION_EXPIRY_DAYS = getattr(settings, "ORGANIZATION_INVITATION_EXPIRY_DAYS", 7)
MEMBER_LIMIT = getattr(settings, "ORGANIZATION_MEMBER_LIMIT", 50)


def create_organization(user, name, description=""):
    """
    Create an organization with *user* as owner.
    Returns the Organization instance.
    """
    from apps.users.models.organization import Organization, OrganizationMembership

    slug = _unique_slug(name)

    with transaction.atomic():
        org = Organization.objects.create(
            name=name,
            slug=slug,
            description=description,
            owner=user,
        )
        OrganizationMembership.objects.create(
            organization=org,
            user=user,
            role="owner",
        )
    logger.info("Organization '%s' created by user id=%s", name, user.pk)
    return org


def create_default_organization(user):
    """Create a default personal organization for a newly registered user."""
    name = f"{user.first_name or user.username}'s Organization"
    return create_organization(user, name)


def invite_member(organization, email, role, invited_by):
    """
    Create an invitation and send the email.
    Returns (invitation, error_message).
    """
    from apps.users.models.organization import (
        OrganizationInvitation,
        OrganizationMembership,
    )
    from apps.users.services.email_service import send_invitation_email

    # Check member limit
    current_count = OrganizationMembership.objects.filter(
        organization=organization, is_active=True
    ).count()
    if current_count >= MEMBER_LIMIT:
        return None, f"Organization has reached the member limit ({MEMBER_LIMIT})."

    # Check for existing active membership via email
    from django.contrib.auth import get_user_model

    User = get_user_model()
    existing_user = User.objects.filter(email=email).first()
    if existing_user:
        already_member = OrganizationMembership.objects.filter(
            organization=organization, user=existing_user, is_active=True
        ).exists()
        if already_member:
            return None, "This user is already a member of the organization."

    # Revoke any previous pending invitations for the same email + org
    OrganizationInvitation.objects.filter(
        organization=organization, email=email, status="pending"
    ).update(status="revoked")

    invitation = OrganizationInvitation.objects.create(
        organization=organization,
        email=email,
        role=role,
        invited_by=invited_by,
        expires_at=timezone.now() + timedelta(days=INVITATION_EXPIRY_DAYS),
    )

    send_invitation_email(invitation)
    logger.info(
        "Invitation sent to %s for org '%s' (role=%s)",
        email,
        organization.name,
        role,
    )
    return invitation, None


def accept_invitation(token, user):
    """
    Accept an invitation by its token.
    Returns (membership, error_message).
    """
    from apps.users.models.organization import (
        OrganizationInvitation,
        OrganizationMembership,
    )

    try:
        invitation = OrganizationInvitation.objects.select_related("organization").get(
            token=token, status="pending"
        )
    except OrganizationInvitation.DoesNotExist:
        return None, "Invitation not found or already used."

    if timezone.now() > invitation.expires_at:
        invitation.status = "expired"
        invitation.save(update_fields=["status"])
        return None, "This invitation has expired."

    if invitation.email != user.email:
        return None, "This invitation was sent to a different email address."

    with transaction.atomic():
        membership, created = OrganizationMembership.objects.get_or_create(
            organization=invitation.organization,
            user=user,
            defaults={"role": invitation.role, "is_active": True},
        )
        if not created and not membership.is_active:
            membership.is_active = True
            membership.role = invitation.role
            membership.save(update_fields=["is_active", "role", "updated_at"])

        invitation.status = "accepted"
        invitation.accepted_at = timezone.now()
        invitation.save(update_fields=["status", "accepted_at"])

    logger.info(
        "User id=%s accepted invitation to org '%s'",
        user.pk,
        invitation.organization.name,
    )
    return membership, None


def remove_member(organization, user_to_remove, removed_by):
    """
    Remove a member from an organization.
    Returns (success, error_message).
    """
    from apps.users.models.organization import OrganizationMembership

    if organization.owner == user_to_remove:
        return False, "Cannot remove the organization owner."

    try:
        membership = OrganizationMembership.objects.get(
            organization=organization, user=user_to_remove, is_active=True
        )
    except OrganizationMembership.DoesNotExist:
        return False, "User is not a member of this organization."

    membership.is_active = False
    membership.save(update_fields=["is_active", "updated_at"])

    logger.info(
        "User id=%s removed from org '%s' by user id=%s",
        user_to_remove.pk,
        organization.name,
        removed_by.pk,
    )
    return True, None


def transfer_ownership(organization, new_owner, current_owner):
    """
    Transfer organization ownership.
    Returns (success, error_message).
    """
    from apps.users.models.organization import OrganizationMembership

    if organization.owner != current_owner:
        return False, "Only the current owner can transfer ownership."

    # Ensure new_owner is a member
    try:
        new_membership = OrganizationMembership.objects.get(
            organization=organization, user=new_owner, is_active=True
        )
    except OrganizationMembership.DoesNotExist:
        return False, "New owner must be an active member of the organization."

    with transaction.atomic():
        # Demote current owner to admin
        old_membership = OrganizationMembership.objects.get(
            organization=organization, user=current_owner
        )
        old_membership.role = "admin"
        old_membership.save(update_fields=["role", "updated_at"])

        # Promote new owner
        new_membership.role = "owner"
        new_membership.save(update_fields=["role", "updated_at"])

        organization.owner = new_owner
        organization.save(update_fields=["owner", "updated_at"])

    logger.info(
        "Ownership of org '%s' transferred from user id=%s to user id=%s",
        organization.name,
        current_owner.pk,
        new_owner.pk,
    )
    return True, None


def _unique_slug(name):
    """Generate a unique slug from a name."""
    from apps.users.models.organization import Organization

    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    while Organization.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
