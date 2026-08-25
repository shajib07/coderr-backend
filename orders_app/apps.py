"""Orders app configuration."""

from django.apps import AppConfig


class OrdersAppConfig(AppConfig):
    """Configure the orders domain app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "orders_app"

