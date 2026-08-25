"""Admin registrations for offer models."""

from django.contrib import admin

from offers_app.models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """Edit offer tiers alongside their parent offer."""

    model = OfferDetail
    extra = 0


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Expose offers and their details in Django admin."""

    list_display = ["title", "user", "updated_at"]
    search_fields = ["title", "description", "user__username"]
    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Expose individual offer tiers in Django admin."""

    list_display = ["title", "offer", "offer_type", "price"]
    list_filter = ["offer_type"]
