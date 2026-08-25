"""Views for profile endpoints."""

from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from auth_app.models import User
from profile_app.api.permissions import IsProfileOwnerOrReadOnly
from profile_app.api.serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer,
    ProfileSerializer,
)
from profile_app.models import Profile


class ProfileDetailView(RetrieveUpdateAPIView):
    """Retrieve profiles and allow owner-only partial updates."""

    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch", "head", "options"]


class ProfileListView(ListAPIView):
    """List profiles for one configured account type."""

    permission_classes = [IsAuthenticated]
    user_type = None

    def get_queryset(self):
        return Profile.objects.select_related("user").filter(user__type=self.user_type)


class BusinessProfileListView(ProfileListView):
    """List all business profiles."""

    serializer_class = BusinessProfileSerializer
    user_type = User.UserType.BUSINESS


class CustomerProfileListView(ProfileListView):
    """List all customer profiles."""

    serializer_class = CustomerProfileSerializer
    user_type = User.UserType.CUSTOMER
