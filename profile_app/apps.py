"""Profile app configuration."""

from django.apps import AppConfig


class ProfileAppConfig(AppConfig):
    """Configure the profile domain app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "profile_app"

