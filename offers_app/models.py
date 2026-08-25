"""Offer domain models."""

from django.conf import settings
from django.db import models


class Offer(models.Model):
    """A service offer created by a business user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offers",
    )
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to="offers/", blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    """One of the three purchasable tiers belonging to an offer."""

    class OfferType(models.TextChoices):
        BASIC = "basic", "Basic"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="details",
    )
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10, choices=OfferType.choices)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"],
                name="unique_offer_type_per_offer",
            )
        ]

    def __str__(self):
        return f"{self.offer.title} - {self.get_offer_type_display()}"
