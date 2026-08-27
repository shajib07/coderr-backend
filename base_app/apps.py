"""Base information app configuration."""

from django.apps import AppConfig


class BaseAppConfig(AppConfig):
    """Configure cross-domain platform information."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "base_app"

