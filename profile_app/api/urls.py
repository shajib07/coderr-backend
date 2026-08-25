"""Profile API routes."""

from django.urls import path

from profile_app.api.views import (
    BusinessProfileListView,
    CustomerProfileListView,
    ProfileDetailView,
)

app_name = "profile_api"
urlpatterns = [
    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="detail"),
    path(
        "profiles/business/",
        BusinessProfileListView.as_view(),
        name="business-list",
    ),
    path(
        "profiles/customer/",
        CustomerProfileListView.as_view(),
        name="customer-list",
    ),
]
