"""Offers app configuration."""

from django.apps import AppConfig


class OffersAppConfig(AppConfig):
    """Configure the offers domain app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "offers_app"

