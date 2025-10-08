from rest_framework import permissions


class IsOwnerOrManager(permissions.BasePermission):
    """
    Custom permission to only allow owners or managers to access certain views.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["user", "admin"]
        )


class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission for admin or owner access only.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["admin", "user"]
        )


class CanManageBatches(permissions.BasePermission):
    """
    Custom permission for Batches management.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["user", "admin"]
        )


class CanViewReports(permissions.BasePermission):
    """
    Custom permission for viewing reports.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["user", "admin"]
        )
