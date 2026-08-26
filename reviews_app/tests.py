"""Tests for review behavior."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from reviews_app.models import Review


class ReviewApiTests(APITestCase):
    """Verify review listing, creation, filtering, editing, and deletion."""

    def setUp(self):
        self.customer = self.create_user("customer", User.UserType.CUSTOMER)
        self.other_customer = self.create_user("buyer", User.UserType.CUSTOMER)
        self.business = self.create_user("business", User.UserType.BUSINESS)
        self.other_business = self.create_user("agency", User.UserType.BUSINESS)
        self.review = Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description="Very professional service.",
        )

    def create_user(self, username, user_type):
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="A-secure-password-123!",
            type=user_type,
        )

    def test_authenticated_user_can_list_all_reviews(self):
        self.client.force_authenticate(self.other_business)

        response = self.client.get(reverse("reviews_api:list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["reviewer"], self.customer.pk)

    def test_review_list_requires_authentication(self):
        response = self.client.get(reverse("reviews_api:list-create"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_list_supports_filters_and_ordering(self):
        second = Review.objects.create(
            business_user=self.other_business,
            reviewer=self.customer,
            rating=5,
            description="Excellent.",
        )
        self.client.force_authenticate(self.business)
        url = reverse("reviews_api:list-create")
        query = (
            f"?reviewer_id={self.customer.pk}"
            f"&business_user_id={second.business_user_id}"
        )

        response = self.client.get(url + query + "&ordering=-rating")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], second.pk)

    def test_invalid_filter_returns_bad_request(self):
        self.client.force_authenticate(self.customer)
        url = reverse("reviews_api:list-create")

        response = self.client.get(url + "?reviewer_id=invalid")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_can_create_review_for_business_user(self):
        self.client.force_authenticate(self.other_customer)
        data = {
            "business_user": self.business.pk,
            "rating": 5,
            "description": "Excellent work!",
        }

        response = self.client.post(reverse("reviews_api:list-create"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review = Review.objects.get(pk=response.data["id"])
        self.assertEqual(review.reviewer, self.other_customer)
        self.assertEqual(review.business_user, self.business)

    def test_customer_cannot_review_same_business_twice(self):
        self.client.force_authenticate(self.customer)
        data = {
            "business_user": self.business.pk,
            "rating": 3,
            "description": "A second review.",
        }

        response = self.client.post(reverse("reviews_api:list-create"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_business_user_cannot_create_review(self):
        data = {
            "business_user": self.other_business.pk,
            "rating": 5,
            "description": "Not allowed.",
        }

        anonymous_response = self.client.post(reverse("reviews_api:list-create"), data)
        self.client.force_authenticate(self.business)
        business_response = self.client.post(reverse("reviews_api:list-create"), data)

        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(business_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_review_requires_business_target_and_valid_rating(self):
        self.client.force_authenticate(self.other_customer)
        url = reverse("reviews_api:list-create")
        customer_target = {
            "business_user": self.customer.pk,
            "rating": 4,
            "description": "Invalid target.",
        }
        invalid_rating = {
            "business_user": self.business.pk,
            "rating": 6,
            "description": "Invalid rating.",
        }

        target_response = self.client.post(url, customer_target)
        rating_response = self.client.post(url, invalid_rating)

        self.assertEqual(target_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(rating_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_author_can_update_rating_and_description(self):
        self.client.force_authenticate(self.customer)
        url = reverse("reviews_api:detail", args=[self.review.pk])

        response = self.client.patch(url, {"rating": 5, "description": "Better!"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.description, "Better!")

    def test_non_author_and_anonymous_user_cannot_update_review(self):
        url = reverse("reviews_api:detail", args=[self.review.pk])

        anonymous_response = self.client.patch(url, {"rating": 2})
        self.client.force_authenticate(self.other_customer)
        other_response = self.client.patch(url, {"rating": 2})

        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(other_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_rejects_invalid_rating_and_immutable_fields(self):
        self.client.force_authenticate(self.customer)
        url = reverse("reviews_api:detail", args=[self.review.pk])

        rating_response = self.client.patch(url, {"rating": 0})
        field_response = self.client.patch(
            url,
            {"business_user": self.other_business.pk},
        )

        self.assertEqual(rating_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(field_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_author_can_delete_review(self):
        self.client.force_authenticate(self.customer)
        url = reverse("reviews_api:detail", args=[self.review.pk])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

    def test_review_string_identifies_parties_and_rating(self):
        expected = "customer rated business: 4"

        self.assertEqual(str(self.review), expected)
