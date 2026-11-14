"""Regression tests for the Part 2 navigation feedback."""

from django.test import TestCase
from .models import User, Store, Product, Review


class PartTwoNavigationTests(TestCase):
    """Check catalogue entry points and vendor-wide review visibility."""

    def setUp(self):
        """Create two separate catalogues and buyer feedback."""
        self.buyer = User.objects.create_user(
            "navbuyer", email="nb@example.com"
        )
        self.vendor = User.objects.create_user(
            "navvendor", email="nv@example.com", role="vendor"
        )
        other = User.objects.create_user(
            "navother", email="no@example.com", role="vendor"
        )
        self.store = Store.objects.create(
            name="Owned store", vendor=self.vendor
        )
        self.other_store = Store.objects.create(
            name="Other store", vendor=other
        )
        self.product = Product.objects.create(
            store=self.store,
            name="Owned item",
            description="Text",
            price=10,
            stock=4,
        )
        other_product = Product.objects.create(
            store=self.other_store,
            name="Other item",
            description="Text",
            price=10,
            stock=4,
        )
        Review.objects.create(
            product=self.product,
            buyer=self.buyer,
            rating=4,
            content="Owned feedback",
        )
        Review.objects.create(
            product=other_product,
            buyer=self.buyer,
            rating=3,
            content="Other feedback",
        )

    def test_buyer_menu_and_vendor_to_store_flow(self):
        """Expose all three buyer catalogue entry points."""
        self.client.force_login(self.buyer)
        response = self.client.get("/")
        for label in ["Vendors", "Stores", "Products", "Cart"]:
            self.assertContains(response, ">" + label + "</a>")
        self.assertContains(self.client.get("/vendors/"), "navvendor")
        response = self.client.get(f"/vendors/{self.vendor.pk}/stores/")
        self.assertContains(response, "Owned store")
        self.assertNotContains(response, "Other store")
        self.assertContains(
            self.client.get(f"/stores/{self.store.pk}/"), "Owned item"
        )

    def test_vendor_lists_only_own_stores_products_and_reviews(self):
        """Keep management entry points scoped to the signed-in vendor."""
        self.client.force_login(self.vendor)
        for url, included, excluded in [
            ("/stores/", "Owned store", "Other store"),
            ("/products/", "Owned item", "Other item"),
            ("/reviews/", "Owned feedback", "Other feedback"),
        ]:
            response = self.client.get(url)
            self.assertContains(response, included)
            self.assertNotContains(response, excluded)

    def test_buyer_cannot_open_vendor_review_overview(self):
        """Reject buyer access to the vendor review overview."""
        self.client.force_login(self.buyer)
        self.assertEqual(self.client.get("/reviews/").status_code, 403)
