"""Tests for authentication behavior."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User


class RegistrationTests(APITestCase):
    """Verify public account registration."""

    url = reverse("auth_api:registration")

    def registration_data(self):
        return {
            "username": "customer_one",
            "email": "customer@example.com",
            "password": "A-secure-password-123!",
            "repeated_password": "A-secure-password-123!",
            "type": User.UserType.CUSTOMER,
        }

    def test_registration_creates_user_and_returns_token(self):
        response = self.client.post(self.url, self.registration_data())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="customer_one")
        self.assertTrue(user.check_password("A-secure-password-123!"))
        self.assertEqual(response.data["user_id"], user.pk)
        self.assertIn("token", response.data)

    def test_registration_rejects_mismatched_passwords(self):
        data = self.registration_data()
        data["repeated_password"] = "a-different-password"

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.exists())


class LoginTests(APITestCase):
    """Verify username and password login."""

    url = reverse("auth_api:login")

    def setUp(self):
        self.user = User.objects.create_user(
            username="business_one",
            email="business@example.com",
            password="A-secure-password-123!",
            type=User.UserType.BUSINESS,
        )

    def test_login_returns_user_data_and_token(self):
        response = self.client.post(
            self.url,
            {"username": self.user.username, "password": "A-secure-password-123!"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["user_id"], self.user.pk)
        self.assertIn("token", response.data)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            self.url,
            {"username": self.user.username, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
