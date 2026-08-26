"""Views for order endpoints."""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from auth_app.models import User
from offers_app.models import OfferDetail
from orders_app.api.permissions import IsCustomerUser, IsOrderBusinessUser
from orders_app.api.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
)
from orders_app.models import Order
from orders_app.services import create_order_from_detail


class OrderListCreateView(ListCreateAPIView):
    """List a user's orders and create customer orders."""

    queryset = Order.objects.select_related("customer_user", "business_user")

    def get_queryset(self):
        user = self.request.user
        parties = Q(customer_user=user) | Q(business_user=user)
        return super().get_queryset().filter(parties)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsCustomerUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        detail = get_object_or_404(
            OfferDetail.objects.select_related("offer__user"),
            pk=serializer.validated_data["offer_detail_id"],
        )
        order = create_order_from_detail(request.user, detail)
        return Response(OrderSerializer(order).data, status=HTTP_201_CREATED)


class OrderDetailView(RetrieveUpdateDestroyAPIView):
    """Update order status or allow staff to delete an order."""

    queryset = Order.objects.select_related("customer_user", "business_user")
    http_method_names = ["patch", "delete", "head", "options"]

    def get_serializer_class(self):
        return OrderUpdateSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return [IsOrderBusinessUser()]


class OrderCountView(APIView):
    """Count orders of one status for a verified business user."""

    permission_classes = [IsAuthenticated]
    order_status = None
    response_key = None

    def get(self, request, business_user_id):
        business_user = get_object_or_404(
            User,
            pk=business_user_id,
            type=User.UserType.BUSINESS,
        )
        count = Order.objects.filter(
            business_user=business_user,
            status=self.order_status,
        ).count()
        return Response({self.response_key: count})


class ActiveOrderCountView(OrderCountView):
    """Count in-progress orders for a business user."""

    order_status = Order.Status.IN_PROGRESS
    response_key = "order_count"


class CompletedOrderCountView(OrderCountView):
    """Count completed orders for a business user."""

    order_status = Order.Status.COMPLETED
    response_key = "completed_order_count"
