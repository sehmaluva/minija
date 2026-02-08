"""Permission classes for the users app (role-based AND organization-based)."""

from rest_framework import permissions


# ---------------------------------------------------------------------------
# Legacy role-based permissions (used by existing business-app views)
# ---------------------------------------------------------------------------


class IsOwnerOrManager(permissions.BasePermission):
    """Allow access to authenticated users with system role of user or admin."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["user", "admin"]
        )


class IsAdminOrOwner(permissions.BasePermission):
    """Allow access to authenticated system admins or regular users."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["admin", "user"]
        )


class CanManageBatches(permissions.BasePermission):
    """Allow batch management for authenticated users/admins."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["user", "admin"]
        )


class CanViewReports(permissions.BasePermission):
    """Allow report viewing for authenticated users/admins."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["user", "admin"]
        )


# ---------------------------------------------------------------------------
# Organization-scoped permissions
# ---------------------------------------------------------------------------


class IsOrganizationMember(permissions.BasePermission):
    """User must be an active member of the request's organization."""

    def has_permission(self, request, view):
        organization = getattr(request, "organization", None)
        if not organization:
            return False
        return request.user.is_member_of(organization)


class IsOrganizationAdmin(permissions.BasePermission):
    """User must be owner or admin of the request's organization (or the object's org)."""

    def has_permission(self, request, view):
        organization = getattr(request, "organization", None)
        if organization:
            return request.user.is_admin_of(organization)
        # Fall through to object-level check
        return True

    def has_object_permission(self, request, view, obj):
        organization = (
            getattr(obj, "organization", obj) if not isinstance(obj, type) else obj
        )
        from apps.users.models.organization import Organization

        if isinstance(organization, Organization):
            return request.user.is_admin_of(organization)
        return False


class IsOrganizationOwner(permissions.BasePermission):
    """User must be the owner of the organization."""

    def has_permission(self, request, view):
        organization = getattr(request, "organization", None)
        if organization:
            return request.user.is_owner_of(organization)
        return True

    def has_object_permission(self, request, view, obj):
        organization = (
            getattr(obj, "organization", obj) if not isinstance(obj, type) else obj
        )
        from apps.users.models.organization import Organization

        if isinstance(organization, Organization):
            return request.user.is_owner_of(organization)
        return False
