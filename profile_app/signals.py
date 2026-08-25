"""Lifecycle signals for profiles."""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from profile_app.models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_user(sender, instance, created, **kwargs):
    """Create the profile required by every new user account."""
    if created:
        Profile.objects.create(user=instance)
