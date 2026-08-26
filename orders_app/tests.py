"""Tests for order behavior."""

from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import User
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from orders_app.services import create_order_from_detail


class OrderApiTests(APITestCase):
    """Verify order creation, visibility, workflow, deletion, and counts."""

    def setUp(self):
        self.customer = self.create_user("customer", User.UserType.CUSTOMER)
        self.other_customer = self.create_user("buyer", User.UserType.CUSTOMER)
        self.business = self.create_user("business", User.UserType.BUSINESS)
        self.other_business = self.create_user("agency", User.UserType.BUSINESS)
        self.staff = self.create_user("admin", User.UserType.BUSINESS, is_staff=True)
        self.detail = self.create_detail(self.business)
        self.order = create_order_from_detail(self.customer, self.detail)

    def create_user(self, username, user_type, is_staff=False):
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="A-secure-password-123!",
            type=user_type,
            is_staff=is_staff,
        )

    def create_detail(self, business):
        offer = Offer.objects.create(
            user=business,
            title="Logo Design",
            description="Professional logo service",
        )
        return OfferDetail.objects.create(
            offer=offer,
            title="Basic Logo",
            revisions=3,
            delivery_time_in_days=5,
            price="150.00",
            features=["Logo", "Business card"],
            offer_type=OfferDetail.OfferType.BASIC,
        )

    def test_customer_and_business_see_only_related_orders(self):
        unrelated = create_order_from_detail(self.other_customer, self.detail)
        url = reverse("orders_api:list-create")

        self.client.force_authenticate(self.customer)
        customer_response = self.client.get(url)
        self.client.force_authenticate(self.business)
        business_response = self.client.get(url)

        self.assertEqual(len(customer_response.data), 1)
        self.assertEqual(len(business_response.data), 2)
        self.assertIn(unrelated.pk, [item["id"] for item in business_response.data])

    def test_customer_can_create_order_from_offer_detail(self):
        self.client.force_authenticate(self.other_customer)

        response = self.client.post(
            reverse("orders_api:list-create"),
            {"offer_detail_id": self.detail.pk},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(pk=response.data["id"])
        self.assertEqual(order.business_user, self.business)
        self.assertEqual(order.customer_user, self.other_customer)
        self.assertEqual(order.price, Decimal("150.00"))
        self.assertEqual(order.features, ["Logo", "Business card"])

    def test_order_snapshot_is_unchanged_when_offer_detail_changes(self):
        self.detail.price = "999.00"
        self.detail.title = "Changed title"
        self.detail.save()

        self.order.refresh_from_db()

        self.assertEqual(self.order.price, Decimal("150.00"))
        self.assertEqual(self.order.title, "Basic Logo")
        self.assertEqual(str(self.order), f"Order {self.order.pk}: Basic Logo")

    def test_anonymous_and_business_users_cannot_create_orders(self):
        url = reverse("orders_api:list-create")
        data = {"offer_detail_id": self.detail.pk}

        anonymous_response = self.client.post(url, data)
        self.client.force_authenticate(self.business)
        business_response = self.client.post(url, data)

        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(business_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_and_unknown_offer_detail_are_rejected(self):
        self.client.force_authenticate(self.customer)
        url = reverse("orders_api:list-create")

        missing_response = self.client.post(url, {})
        unknown_response = self.client.post(url, {"offer_detail_id": 999999})

        self.assertEqual(missing_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(unknown_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_business_party_can_update_order_status(self):
        self.client.force_authenticate(self.business)
        url = reverse("orders_api:detail", args=[self.order.pk])

        response = self.client.patch(url, {"status": Order.Status.COMPLETED})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.COMPLETED)

    def test_customer_and_unrelated_business_cannot_update_order(self):
        url = reverse("orders_api:detail", args=[self.order.pk])

        anonymous_response = self.client.patch(url, {"status": "completed"})
        self.client.force_authenticate(self.customer)
        customer_response = self.client.patch(url, {"status": "completed"})
        self.client.force_authenticate(self.other_business)
        business_response = self.client.patch(url, {"status": "completed"})

        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(customer_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(business_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_status_update_rejects_invalid_status_and_other_fields(self):
        self.client.force_authenticate(self.business)
        url = reverse("orders_api:detail", args=[self.order.pk])

        status_response = self.client.patch(url, {"status": "unknown"})
        field_response = self.client.patch(url, {"price": "1.00"})

        self.assertEqual(status_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(field_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_staff_can_delete_order(self):
        url = reverse("orders_api:detail", args=[self.order.pk])

        self.client.force_authenticate(self.business)
        forbidden_response = self.client.delete(url)
        self.client.force_authenticate(self.staff)
        deleted_response = self.client.delete(url)

        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deleted_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())

    def test_active_and_completed_counts_are_status_specific(self):
        completed = create_order_from_detail(self.other_customer, self.detail)
        completed.status = Order.Status.COMPLETED
        completed.save()
        self.client.force_authenticate(self.customer)

        active_response = self.client.get(
            reverse("orders_api:active-count", args=[self.business.pk])
        )
        completed_response = self.client.get(
            reverse("orders_api:completed-count", args=[self.business.pk])
        )

        self.assertEqual(active_response.data, {"order_count": 1})
        self.assertEqual(completed_response.data, {"completed_order_count": 1})

    def test_count_endpoint_requires_auth_and_business_id(self):
        active_url = reverse("orders_api:active-count", args=[self.business.pk])
        customer_url = reverse("orders_api:active-count", args=[self.customer.pk])

        anonymous_response = self.client.get(active_url)
        self.client.force_authenticate(self.customer)
        customer_response = self.client.get(customer_url)

        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(customer_response.status_code, status.HTTP_404_NOT_FOUND)
