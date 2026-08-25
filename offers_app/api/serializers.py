"""Serializers for offer endpoints."""

from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail

DETAIL_FIELDS = {
    "title",
    "revisions",
    "delivery_time_in_days",
    "price",
    "features",
    "offer_type",
}
OFFER_TYPES = {choice.value for choice in OfferDetail.OfferType}


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serialize a complete purchasable offer tier."""

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
        required=False,
    )

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {field: {"required": False} for field in DETAIL_FIELDS}


class OfferDetailLinkSerializer(serializers.HyperlinkedModelSerializer):
    """Serialize an offer tier as the documented ID and URL pair."""

    url = serializers.HyperlinkedIdentityField(view_name="offers_api:detail-item")

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]


class OfferWriteSerializer(serializers.ModelSerializer):
    """Create and update offers together with their nested tiers."""

    details = OfferDetailSerializer(many=True, required=True)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]
        read_only_fields = ["id"]

    def validate_details(self, details):
        """Require complete tiers on create and identifiable tiers on update."""
        if self.instance is None:
            self._validate_new_details(details)
        elif any("offer_type" not in detail for detail in details):
            raise serializers.ValidationError("Each updated detail needs offer_type.")
        return details

    def _validate_new_details(self, details):
        if len(details) != 3:
            message = "An offer must contain exactly 3 details."
            raise serializers.ValidationError(message)
        if any(DETAIL_FIELDS - detail.keys() for detail in details):
            raise serializers.ValidationError("Every detail must contain all fields.")
        types = {detail["offer_type"] for detail in details}
        if types != OFFER_TYPES:
            raise serializers.ValidationError("Use basic, standard, and premium once.")

    @transaction.atomic
    def create(self, validated_data):
        details = validated_data.pop("details", [])
        offer = Offer.objects.create(**validated_data)
        OfferDetail.objects.bulk_create(
            OfferDetail(offer=offer, **detail) for detail in details
        )
        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        details = validated_data.pop("details", None)
        offer = super().update(instance, validated_data)
        if details is not None:
            self._update_details(offer, details)
        return offer

    def _update_details(self, offer, details):
        for values in details:
            offer_type = values.pop("offer_type")
            detail = offer.details.get(offer_type=offer_type)
            for field, value in values.items():
                setattr(detail, field, value)
            detail.save()


class OfferReadSerializer(serializers.ModelSerializer):
    """Serialize offer metadata and links to its purchasable tiers."""

    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(10, 2, coerce_to_string=False, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]


class OfferListSerializer(OfferReadSerializer):
    """Add creator summary data to offers in the public list."""

    user_details = serializers.SerializerMethodField()

    class Meta(OfferReadSerializer.Meta):
        fields = OfferReadSerializer.Meta.fields + ["user_details"]

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username,
        }
