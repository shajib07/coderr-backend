"""Admin registrations for order models."""

from django.contrib import admin

from orders_app.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Expose order parties and workflow status in Django admin."""

    list_display = ["id", "title", "customer_user", "business_user", "status"]
    list_filter = ["status", "offer_type"]
    search_fields = ["title", "customer_user__username", "business_user__username"]
