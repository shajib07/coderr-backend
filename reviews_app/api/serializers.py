"""Serializers for review endpoints."""

from rest_framework import serializers

from auth_app.models import User
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize review creation and the documented response fields."""

    business_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(type=User.UserType.BUSINESS)
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reviewer", "created_at", "updated_at"]

    def validate_business_user(self, business_user):
        """Prevent duplicate reviews for one customer/business pair."""
        reviewer = self.context["request"].user
        duplicate = Review.objects.filter(
            business_user=business_user,
            reviewer=reviewer,
        ).exists()
        if duplicate:
            message = "You already reviewed this business user."
            raise serializers.ValidationError(message)
        return business_user


class ReviewUpdateSerializer(ReviewSerializer):
    """Restrict review updates to rating and description."""

    business_user = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_internal_value(self, data):
        """Reject fields outside the documented PATCH contract."""
        unexpected = set(data) - {"rating", "description"}
        if unexpected:
            raise serializers.ValidationError(
                {field: "This field may not be updated." for field in unexpected}
            )
        return super().to_internal_value(data)
