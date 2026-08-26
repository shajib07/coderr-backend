"""Serializers for order endpoints."""

from rest_framework import serializers

from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serialize the documented order snapshot."""

    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """Validate the offer tier selected for a new order."""

    offer_detail_id = serializers.IntegerField(min_value=1)


class OrderUpdateSerializer(OrderSerializer):
    """Allow only the workflow status to be changed."""

    status = serializers.ChoiceField(choices=Order.Status.choices)

    class Meta(OrderSerializer.Meta):
        read_only_fields = [
            field for field in OrderSerializer.Meta.fields if field != "status"
        ]

    def to_internal_value(self, data):
        """Reject fields outside the documented status-only PATCH contract."""
        unexpected = set(data) - {"status"}
        if unexpected:
            raise serializers.ValidationError(
                {field: "This field may not be updated." for field in unexpected}
            )
        return super().to_internal_value(data)
