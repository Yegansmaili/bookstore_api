from rest_framework import permissions


class IsAdminOrPostOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_staff)
        if request.method == 'POST':
            return True
