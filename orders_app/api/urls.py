"""Order API routes."""

from django.urls import path

from orders_app.api.views import (
    ActiveOrderCountView,
    CompletedOrderCountView,
    OrderDetailView,
    OrderListCreateView,
)

app_name = "orders_api"
urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="list-create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="detail"),
    path(
        "order-count/<int:business_user_id>/",
        ActiveOrderCountView.as_view(),
        name="active-count",
    ),
    path(
        "completed-order-count/<int:business_user_id>/",
        CompletedOrderCountView.as_view(),
        name="completed-count",
    ),
]
