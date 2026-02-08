"""Middleware that attaches organization context to every authenticated request."""

import logging

logger = logging.getLogger(__name__)


def _get_membership_model():
    """Lazy import to avoid circular/premature model imports during Django setup."""
    from apps.users.models.organization import OrganizationMembership

    return OrganizationMembership


class OrganizationMiddleware:
    """
    Reads ``X-Organization-ID`` from the request header (or falls back to the
    user's first active organization) and attaches:

    - ``request.organization``       – the Organization instance (or None)
    - ``request.organization_role``   – the user's role string (or None)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        request.organization_role = None

        if hasattr(request, "user") and request.user.is_authenticated:
            OrganizationMembership = _get_membership_model()
            org_id = request.headers.get("X-Organization-ID")

            if org_id:
                try:
                    membership = OrganizationMembership.objects.select_related(
                        "organization"
                    ).get(
                        organization_id=org_id,
                        user=request.user,
                        is_active=True,
                        organization__is_active=True,
                    )
                    request.organization = membership.organization
                    request.organization_role = membership.role
                except OrganizationMembership.DoesNotExist:
                    logger.debug(
                        "User id=%s has no active membership in org id=%s",
                        request.user.pk,
                        org_id,
                    )
            else:
                # Auto-select first active organization
                first = (
                    OrganizationMembership.objects.filter(
                        user=request.user,
                        is_active=True,
                        organization__is_active=True,
                    )
                    .select_related("organization")
                    .first()
                )
                if first:
                    request.organization = first.organization
                    request.organization_role = first.role

        return self.get_response(request)
