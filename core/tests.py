"""Project-level smoke tests."""

from django.test import SimpleTestCase
from django.urls import reverse


class AdminRoutingTests(SimpleTestCase):
    """Verify that the admin environment is wired into central routing."""

    def test_admin_route_is_available(self):
        self.assertEqual(reverse("admin:index"), "/admin/")

