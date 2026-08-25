"""Tests for profile behavior."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from profile_app.models import Profile


class ProfileApiTests(APITestCase):
    """Verify profile detail, update, permissions, and typed lists."""

    def setUp(self):
        self.customer = self.create_user("customer", User.UserType.CUSTOMER)
        self.business = self.create_user("business", User.UserType.BUSINESS)

    def create_user(self, username, user_type):
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="A-secure-password-123!",
            type=user_type,
        )

    def test_new_user_receives_profile(self):
        self.assertTrue(Profile.objects.filter(user=self.customer).exists())
        self.assertEqual(str(self.customer.profile), "Profile for customer")

    def test_profile_detail_requires_authentication(self):
        url = reverse("profile_api:detail", args=[self.customer.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_read_another_profile(self):
        self.client.force_authenticate(self.business)
        url = reverse("profile_api:detail", args=[self.customer.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.customer.pk)
        self.assertEqual(response.data["first_name"], "")
        self.assertEqual(response.data["working_hours"], "")

    def test_owner_can_update_profile_and_user_fields(self):
        self.client.force_authenticate(self.customer)
        url = reverse("profile_api:detail", args=[self.customer.pk])
        data = {
            "first_name": "Jane",
            "email": "jane@example.com",
            "location": "Berlin",
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, "Jane")
        self.assertEqual(self.customer.email, "jane@example.com")
        self.assertEqual(self.customer.profile.location, "Berlin")

    def test_owner_can_update_only_profile_fields(self):
        self.client.force_authenticate(self.customer)
        url = reverse("profile_api:detail", args=[self.customer.pk])

        response = self.client.patch(url, {"tel": "12345"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.profile.refresh_from_db()
        self.assertEqual(self.customer.profile.tel, "12345")

    def test_user_cannot_update_another_profile(self):
        self.client.force_authenticate(self.customer)
        url = reverse("profile_api:detail", args=[self.business.pk])

        response = self.client.patch(url, {"location": "Hamburg"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_email_is_rejected(self):
        self.client.force_authenticate(self.customer)
        url = reverse("profile_api:detail", args=[self.customer.pk])

        response = self.client.patch(url, {"email": self.business.email})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_business_list_contains_only_business_profiles(self):
        self.client.force_authenticate(self.customer)

        response = self.client.get(reverse("profile_api:business-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["type"], User.UserType.BUSINESS)
        self.assertIn("working_hours", response.data[0])

    def test_customer_list_contains_only_customer_profiles(self):
        self.client.force_authenticate(self.business)

        response = self.client.get(reverse("profile_api:customer-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["type"], User.UserType.CUSTOMER)
        self.assertIn("uploaded_at", response.data[0])
