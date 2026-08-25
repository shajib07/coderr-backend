"""Serializers for profile endpoints."""

from rest_framework import serializers

from auth_app.models import User
from profile_app.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serialize the complete profile detail and update contract."""

    user = serializers.IntegerField(source="user.pk", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
        allow_blank=True,
    )
    type = serializers.CharField(source="user.type", read_only=True)
    email = serializers.EmailField(source="user.email", required=False)

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_email(self, value):
        """Keep email addresses unique while allowing the current value."""
        user_pk = self.instance.user_id if self.instance else None
        duplicate = User.objects.exclude(pk=user_pk).filter(email=value).exists()
        if duplicate:
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def update(self, instance, validated_data):
        """Update profile fields and writable fields stored on its user."""
        user_data = validated_data.pop("user", {})
        profile = super().update(instance, validated_data)
        for field, value in user_data.items():
            setattr(profile.user, field, value)
        if user_data:
            profile.user.save(update_fields=user_data.keys())
        return profile


class BusinessProfileSerializer(serializers.ModelSerializer):
    """Serialize the documented business profile list shape."""

    user = serializers.IntegerField(source="user.pk", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    type = serializers.CharField(source="user.type", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Serialize the documented customer profile list shape."""

    user = serializers.IntegerField(source="user.pk", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    type = serializers.CharField(source="user.type", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]
