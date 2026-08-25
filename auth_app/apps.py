"""Authentication app configuration."""

from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """Configure the authentication domain app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_app"

