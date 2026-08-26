"""Review API routes."""

from django.urls import path

from reviews_app.api.views import ReviewDetailView, ReviewListCreateView

app_name = "reviews_api"
urlpatterns = [
    path("reviews/", ReviewListCreateView.as_view(), name="list-create"),
    path("reviews/<int:pk>/", ReviewDetailView.as_view(), name="detail"),
]
