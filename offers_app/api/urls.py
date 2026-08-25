"""Offer API routes."""

from django.urls import path

from offers_app.api.views import (
    OfferDetailItemView,
    OfferDetailView,
    OfferListCreateView,
)

app_name = "offers_api"
urlpatterns = [
    path("offers/", OfferListCreateView.as_view(), name="list-create"),
    path("offers/<int:pk>/", OfferDetailView.as_view(), name="detail"),
    path(
        "offerdetails/<int:pk>/",
        OfferDetailItemView.as_view(),
        name="detail-item",
    ),
]
