"""Authentication domain models."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """A Coderr user with a customer or business account type."""

    class UserType(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        BUSINESS = "business", "Business"

    email = models.EmailField(unique=True)
    type = models.CharField(max_length=10, choices=UserType.choices)
