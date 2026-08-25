"""Custom permissions for profile endpoints."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsProfileOwnerOrReadOnly(BasePermission):
    """Allow authenticated reads but restrict writes to the profile owner."""

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.user == request.user
