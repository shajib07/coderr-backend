"""Admin registrations for profile models."""

from django.contrib import admin

from profile_app.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Make profiles searchable and editable in Django admin."""

    list_display = ["user", "location", "created_at"]
    search_fields = ["user__username", "user__email", "location"]
