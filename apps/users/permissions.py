from rest_framework import permissions

class IsOwnerOrManager(permissions.BasePermission):
    """
    Custom permission to only allow owners or managers to access certain views.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['owner', 'manager', 'admin']

class IsVeterinarianOrManager(permissions.BasePermission):
    """
    Custom permission for veterinarian or manager access.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['veterinarian', 'manager', 'admin', 'owner']

class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission for admin or owner access only.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'owner']

class CanManageFlocks(permissions.BasePermission):
    """
    Custom permission for flock management.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['manager', 'admin', 'owner']

class CanViewReports(permissions.BasePermission):
    """
    Custom permission for viewing reports.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['manager', 'admin', 'owner', 'veterinarian']
