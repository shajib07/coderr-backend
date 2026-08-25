"""Reviews app configuration."""

from django.apps import AppConfig


class ReviewsAppConfig(AppConfig):
    """Configure the reviews domain app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "reviews_app"

