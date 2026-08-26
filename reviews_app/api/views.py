"""Views for review endpoints."""

from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from reviews_app.api.filters import ReviewFilterBackend
from reviews_app.api.permissions import IsCustomerUser, IsReviewAuthor
from reviews_app.api.serializers import ReviewSerializer, ReviewUpdateSerializer
from reviews_app.models import Review


class ReviewListCreateView(ListCreateAPIView):
    """List authenticated reviews and create customer reviews."""

    queryset = Review.objects.select_related("business_user", "reviewer")
    serializer_class = ReviewSerializer
    filter_backends = [ReviewFilterBackend, OrderingFilter]
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsCustomerUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    """Allow author-only review updates and deletion."""

    queryset = Review.objects.select_related("business_user", "reviewer")
    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsReviewAuthor]
    http_method_names = ["patch", "delete", "head", "options"]
