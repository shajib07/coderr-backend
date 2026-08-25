"""Tests for offer behavior."""

from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from offers_app.models import Offer, OfferDetail


class OfferApiTests(APITestCase):
    """Verify offer CRUD, filtering, permissions, and tier retrieval."""

    def setUp(self):
        self.business = self.create_user("business", User.UserType.BUSINESS)
        self.other_business = self.create_user("other", User.UserType.BUSINESS)
        self.customer = self.create_user("customer", User.UserType.CUSTOMER)
        self.offer = self.create_offer(self.business, "Website Design")

    def create_user(self, username, user_type):
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="A-secure-password-123!",
            type=user_type,
        )

    def detail_data(self, offer_type, price, delivery_time):
        return {
            "title": f"{offer_type.title()} package",
            "revisions": 2,
            "delivery_time_in_days": delivery_time,
            "price": price,
            "features": ["Feature one"],
            "offer_type": offer_type,
        }

    def offer_data(self, title="Logo Design"):
        return {
            "title": title,
            "description": "Professional design service",
            "details": [
                self.detail_data("basic", "100.00", 5),
                self.detail_data("standard", "200.00", 7),
                self.detail_data("premium", "300.00", 10),
            ],
        }

    def create_offer(self, user, title):
        offer = Offer.objects.create(
            user=user,
            title=title,
            description="Professional website service",
        )
        for detail in self.offer_data()["details"]:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

    def test_public_offer_list_is_paginated_with_aggregates(self):
        response = self.client.get(reverse("offers_api:list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        offer = response.data["results"][0]
        self.assertEqual(offer["min_price"], Decimal("100.00"))
        self.assertEqual(offer["min_delivery_time"], 5)
        self.assertEqual(offer["user_details"]["username"], "business")

    def test_offer_list_supports_documented_filters(self):
        self.create_offer(self.other_business, "Photography")
        url = reverse("offers_api:list-create")
        query = "?creator_id={}&min_price=100&max_delivery_time=5&search=Website"

        response = self.client.get(url + query.format(self.business.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Website Design")

    def test_invalid_filter_returns_bad_request(self):
        url = reverse("offers_api:list-create")

        response = self.client.get(url + "?min_price=invalid")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_integer_filter_returns_bad_request(self):
        url = reverse("offers_api:list-create")

        response = self.client.get(url + "?creator_id=invalid")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_user_cannot_create_offer(self):
        response = self.client.post(
            reverse("offers_api:list-create"),
            self.offer_data(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_business_user_can_create_offer_with_three_tiers(self):
        self.client.force_authenticate(self.business)

        response = self.client.post(
            reverse("offers_api:list-create"),
            self.offer_data(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Offer.objects.get(pk=response.data["id"])
        self.assertEqual(created.user, self.business)
        self.assertEqual(created.details.count(), 3)

    def test_customer_cannot_create_offer(self):
        self.client.force_authenticate(self.customer)

        response = self.client.post(
            reverse("offers_api:list-create"),
            self.offer_data(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_creation_requires_exactly_three_unique_tiers(self):
        self.client.force_authenticate(self.business)
        data = self.offer_data()
        data["details"] = data["details"][:2]

        response = self.client.post(
            reverse("offers_api:list-create"), data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creation_requires_complete_unique_tiers(self):
        self.client.force_authenticate(self.business)
        missing_field = self.offer_data()
        missing_field["details"][0].pop("features")
        duplicate_type = self.offer_data()
        duplicate_type["details"][2]["offer_type"] = "standard"

        missing_response = self.client.post(
            reverse("offers_api:list-create"), missing_field, format="json"
        )
        duplicate_response = self.client.post(
            reverse("offers_api:list-create"), duplicate_type, format="json"
        )

        self.assertEqual(missing_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_user_can_retrieve_offer(self):
        self.client.force_authenticate(self.customer)
        url = reverse("offers_api:detail", args=[self.offer.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.business.pk)
        self.assertEqual(len(response.data["details"]), 3)

    def test_owner_can_patch_offer_and_one_tier(self):
        self.client.force_authenticate(self.business)
        basic = self.offer.details.get(offer_type=OfferDetail.OfferType.BASIC)
        data = {
            "title": "Updated Website Design",
            "details": [{"offer_type": "basic", "price": "120.00"}],
        }

        response = self.client.patch(
            reverse("offers_api:detail", args=[self.offer.pk]), data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        basic.refresh_from_db()
        self.assertEqual(basic.price, Decimal("120.00"))
        self.assertEqual(self.offer.details.count(), 3)

    def test_owner_can_patch_offer_without_tiers(self):
        self.client.force_authenticate(self.business)
        url = reverse("offers_api:detail", args=[self.offer.pk])

        response = self.client.patch(url, {"description": "Updated description"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.description, "Updated description")

    def test_tier_patch_requires_offer_type(self):
        self.client.force_authenticate(self.business)
        url = reverse("offers_api:detail", args=[self.offer.pk])

        response = self.client.patch(
            url,
            {"details": [{"price": "120.00"}]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_owner_cannot_patch_offer(self):
        self.client.force_authenticate(self.other_business)
        url = reverse("offers_api:detail", args=[self.offer.pk])

        response = self.client.patch(url, {"title": "Not allowed"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_offer(self):
        self.client.force_authenticate(self.business)
        url = reverse("offers_api:detail", args=[self.offer.pk])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(pk=self.offer.pk).exists())

    def test_authenticated_user_can_retrieve_offer_detail(self):
        self.client.force_authenticate(self.customer)
        detail = self.offer.details.first()
        url = reverse("offers_api:detail-item", args=[detail.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["offer_type"], detail.offer_type)
        self.assertEqual(str(self.offer), "Website Design")
        self.assertEqual(str(detail), "Website Design - Basic")
