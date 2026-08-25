"""Admin registrations for authentication models."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from auth_app.models import User


@admin.register(User)
class CoderrUserAdmin(UserAdmin):
    """Expose Coderr account types in the Django admin."""

    fieldsets = UserAdmin.fieldsets + (("Coderr", {"fields": ("type",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Coderr", {"fields": ("type",)}),)
