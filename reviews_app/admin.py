"""Admin registrations for review models."""

from django.contrib import admin

from reviews_app.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Expose review parties and ratings in Django admin."""

    list_display = ["reviewer", "business_user", "rating", "updated_at"]
    list_filter = ["rating"]
    search_fields = [
        "reviewer__username",
        "business_user__username",
        "description",
    ]
