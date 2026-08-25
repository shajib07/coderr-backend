"""Custom permissions for offer endpoints."""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from auth_app.models import User


class IsBusinessUser(BasePermission):
    """Allow access only to authenticated business users."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.type == User.UserType.BUSINESS


class IsOfferOwnerOrReadOnly(BasePermission):
    """Allow authenticated reads and owner-only modifications."""

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.user == request.user
