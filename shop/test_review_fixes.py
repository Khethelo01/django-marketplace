"""Regression checks for the assessor's Part 1 review."""

from django.conf import settings
from django.test import TestCase
from .forms import ReviewForm
from .models import User, Store, Product


class ReviewFixTests(TestCase):
    """Check MariaDB defaults, input bounds and buyer navigation."""

    def setUp(self):
        """Create a buyer and stocked product for independent checks."""
        self.buyer = User.objects.create_user(
            "reviewbuyer", email="r@example.com"
        )
        vendor = User.objects.create_user(
            "reviewvendor", email="v@example.com", role="vendor"
        )
        store = Store.objects.create(name="Review store", vendor=vendor)
        self.product = Product.objects.create(
            store=store,
            name="Item",
            description="Test item",
            price="10.00",
            stock=3,
        )

    def test_mariadb_is_default(self):
        """Use the MySQL backend for MariaDB without an engine switch."""
        self.assertEqual(
            settings.DATABASES["default"]["ENGINE"], "django.db.backends.mysql"
        )

    def test_rating_widget_bounds(self):
        """Expose min/max in HTML and reject tampered server input."""
        field = ReviewForm().fields["rating"]
        self.assertEqual(field.widget.attrs["min"], 1)
        self.assertEqual(field.widget.attrs["max"], 5)
        self.assertFalse(
            ReviewForm({"rating": 6, "content": "Text"}).is_valid()
        )

    def test_quantity_bounds_and_cart_menu(self):
        """Limit quantity to stock and show the buyer Cart link."""
        self.client.force_login(self.buyer)
        response = self.client.get(f"/products/{self.product.pk}/")
        self.assertContains(response, 'max="3"')
        self.assertContains(response, 'min="1"')
        self.assertContains(response, ">Cart</a>")

    def test_continue_shopping_next_to_checkout(self):
        """Offer an explicit route back to products from the cart."""
        self.client.force_login(self.buyer)
        self.client.post(f"/cart/add/{self.product.pk}/", {"quantity": 1})
        response = self.client.get("/cart/")
        self.assertContains(response, "Continue Shopping")
        self.assertContains(response, "Checkout")
