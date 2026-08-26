"""Custom permissions for order endpoints."""

from rest_framework.permissions import BasePermission

from auth_app.models import User


class IsCustomerUser(BasePermission):
    """Allow order creation only for authenticated customers."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.type == User.UserType.CUSTOMER


class IsOrderBusinessUser(BasePermission):
    """Allow status changes only by the business party of an order."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.type == User.UserType.BUSINESS

    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user
