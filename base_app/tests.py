"""Tests for public base information."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoTests(APITestCase):
    """Verify public platform statistics and rating rounding."""

    def create_user(self, username, user_type):
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="A-secure-password-123!",
            type=user_type,
        )

    def test_empty_platform_returns_zero_values_publicly(self):
        response = self.client.get(reverse("base_api:info"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "review_count": 0,
                "average_rating": 0.0,
                "business_profile_count": 0,
                "offer_count": 0,
            },
        )

    def test_base_info_aggregates_and_rounds_platform_data(self):
        business = self.create_user("business", User.UserType.BUSINESS)
        second_business = self.create_user("agency", User.UserType.BUSINESS)
        customers = [
            self.create_user(f"customer_{index}", User.UserType.CUSTOMER)
            for index in range(3)
        ]
        Offer.objects.create(user=business, title="Logo", description="Design")
        Offer.objects.create(user=business, title="Web", description="Development")
        for customer, rating in zip(customers, [4, 5, 5], strict=True):
            Review.objects.create(
                business_user=second_business,
                reviewer=customer,
                rating=rating,
                description="Good service",
            )

        response = self.client.get(reverse("base_api:info"))

        self.assertEqual(response.data["review_count"], 3)
        self.assertEqual(response.data["average_rating"], 4.7)
        self.assertEqual(response.data["business_profile_count"], 2)
        self.assertEqual(response.data["offer_count"], 2)

