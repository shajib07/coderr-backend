"""Serializers for authentication endpoints."""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from auth_app.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration data and create a Coderr user."""

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        """Require matching passwords and apply Django's validators."""
        password = attrs["password"]
        if password != attrs.pop("repeated_password"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        validate_password(password)
        return attrs

    def create(self, validated_data):
        """Create a user while ensuring the password is hashed."""
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Authenticate a username and password pair."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Attach the authenticated user to validated data."""
        request = self.context.get("request")
        user = authenticate(request=request, **attrs)
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        attrs["user"] = user
        return attrs
