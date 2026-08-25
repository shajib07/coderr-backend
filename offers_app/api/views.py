"""Views for offer endpoints."""

from django.db.models import Min
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated

from offers_app.api.filters import OfferFilterBackend
from offers_app.api.pagination import OfferPagination
from offers_app.api.permissions import IsBusinessUser, IsOfferOwnerOrReadOnly
from offers_app.api.serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferReadSerializer,
    OfferWriteSerializer,
)
from offers_app.models import Offer, OfferDetail


def offer_queryset():
    """Return offers with creator data and documented aggregate values."""
    return Offer.objects.select_related("user").prefetch_related("details").annotate(
        min_price=Min("details__price"),
        min_delivery_time=Min("details__delivery_time_in_days"),
    )


class OfferListCreateView(ListCreateAPIView):
    """List public offers and create business-owned offers."""

    queryset = offer_queryset()
    pagination_class = OfferPagination
    filter_backends = [OfferFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OfferWriteSerializer
        return OfferListSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsBusinessUser()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfferDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve offers and allow owner-only updates or deletion."""

    queryset = offer_queryset()
    permission_classes = [IsAuthenticated, IsOfferOwnerOrReadOnly]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return OfferWriteSerializer
        return OfferReadSerializer


class OfferDetailItemView(RetrieveAPIView):
    """Retrieve one complete offer tier."""

    queryset = OfferDetail.objects.select_related("offer")
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
