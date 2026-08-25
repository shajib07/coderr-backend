"""Profile domain models."""

from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Additional public information belonging to one Coderr user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    file = models.FileField(upload_to="profiles/", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, default="")
    tel = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"Profile for {self.user.username}"
