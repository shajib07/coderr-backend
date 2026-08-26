"""Custom permissions for review endpoints."""

from rest_framework.permissions import BasePermission

from auth_app.models import User


class IsCustomerUser(BasePermission):
    """Allow review creation only for authenticated customers."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.type == User.UserType.CUSTOMER


class IsReviewAuthor(BasePermission):
    """Allow review changes only by the original reviewer."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
