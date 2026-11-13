from decimal import Decimal
from unittest.mock import patch
import requests
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import User, Store, Product, Order, Review
from .services import create_order, send_invoice
from .functions.jsonplaceholder import get_posts


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class ShopTests(TestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            "vendor", "vendor@example.com", "SafePass!234", role="vendor"
        )
        self.other = User.objects.create_user(
            "other", "other@example.com", "SafePass!234", role="vendor"
        )
        self.buyer = User.objects.create_user(
            "buyer", "buyer@example.com", "SafePass!234"
        )
        self.store = Store.objects.create(vendor=self.vendor, name="Books")
        self.product = Product.objects.create(
            store=self.store,
            name="Book",
            description="A good story",
            price=Decimal("25.50"),
            stock=5,
        )
        self.api = APIClient()

    def test_registration(self):
        response = self.client.post(
            "/register/",
            {
                "username": "newbuyer",
                "email": "new@example.com",
                "role": "buyer",
                "password1": "ComplexPass!234",
                "password2": "ComplexPass!234",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.get(username="newbuyer").check_password(
                "ComplexPass!234"
            )
        )

    def test_buyer_cannot_create_store(self):
        self.client.force_login(self.buyer)
        self.assertEqual(
            self.client.post("/stores/new/", {"name": "Bad"}).status_code, 403
        )

    def test_vendor_creates_store(self):
        self.client.force_login(self.vendor)
        self.client.post("/stores/new/", {"name": "New store"})
        self.assertEqual(
            Store.objects.get(name="New store").vendor, self.vendor
        )

    def test_owner_checks(self):
        self.client.force_login(self.other)
        self.assertEqual(
            self.client.post(f"/stores/{self.store.pk}/edit/", {}).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                f"/stores/{self.store.pk}/products/{self.product.pk}/edit/", {}
            ).status_code,
            404,
        )

    def test_delete_get_is_safe(self):
        self.client.force_login(self.vendor)
        self.client.get(f"/delete/product/{self.product.pk}/")
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_cart_persists(self):
        self.client.force_login(self.buyer)
        self.client.post(f"/cart/add/{self.product.pk}/", {"quantity": "2"})
        self.client.get("/")
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 2)

    def test_negative_cart_quantity_rejected(self):
        self.client.force_login(self.buyer)
        self.client.post(f"/cart/add/{self.product.pk}/", {"quantity": "-1"})
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_checkout_invoice_email_and_stock(self):
        self.client.force_login(self.buyer)
        self.client.post(f"/cart/add/{self.product.pk}/", {"quantity": "2"})
        self.assertEqual(self.client.post("/checkout/").status_code, 302)
        self.assertEqual(Order.objects.get().total, Decimal("51.00"))
        self.assertEqual(self.client.session["cart"], {})
        self.assertEqual(len(mail.outbox), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_stock_failure_rolls_back(self):
        with self.assertRaises(ValueError):
            create_order(self.buyer, {str(self.product.pk): 99})
        self.assertFalse(Order.objects.exists())

    def test_empty_checkout_rejected(self):
        with self.assertRaises(ValueError):
            create_order(self.buyer, {})

    def test_verified_review(self):
        review = Review.objects.create(
            buyer=self.buyer, product=self.product, rating=4, content="Good"
        )
        self.assertFalse(review.verified)
        create_order(self.buyer, {str(self.product.pk): 1})
        self.assertTrue(review.verified)

    def test_invoice_failure_and_retry(self):
        order = create_order(self.buyer, {str(self.product.pk): 1})
        with patch("shop.services.send_mail", side_effect=OSError("offline")):
            self.assertFalse(send_invoice(order))
        self.assertTrue(send_invoice(order))

    def test_password_token_invalidated_after_password_change(self):
        from django.contrib.auth.tokens import default_token_generator

        token = default_token_generator.make_token(self.buyer)
        self.assertTrue(default_token_generator.check_token(self.buyer, token))
        self.buyer.set_password("DifferentPass!234")
        self.buyer.save()
        self.assertFalse(
            default_token_generator.check_token(self.buyer, token)
        )

    def test_api_requires_auth(self):
        self.assertEqual(self.api.get("/api/stores/").status_code, 401)

    def test_api_vendor_create(self):
        self.api.force_authenticate(self.vendor)
        response = self.api.post(
            "/api/stores/", {"name": "API store"}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        response = self.api.post(
            f"/api/stores/{response.data['id']}/products/",
            {
                "name": "Product",
                "description": "Text",
                "price": "20.00",
                "stock": 2,
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_api_write_owner_checks(self):
        for user in [self.buyer, self.other]:
            self.api.force_authenticate(user)
            self.assertEqual(
                self.api.post(
                    f"/api/stores/{self.store.pk}/products/", {}
                ).status_code,
                403,
            )

    def test_api_both_roles_can_read(self):
        for user in [self.buyer, self.vendor]:
            self.api.force_authenticate(user)
            self.assertEqual(self.api.get("/api/stores/").status_code, 200)
            self.assertEqual(
                self.api.get(
                    f"/api/stores/{self.store.pk}/products/"
                ).status_code,
                200,
            )

    def test_api_review_owner_scope(self):
        Review.objects.create(
            buyer=self.buyer, product=self.product, rating=5, content="Good"
        )
        self.api.force_authenticate(self.other)
        self.assertEqual(self.api.get("/api/reviews/").data, [])
        self.api.force_authenticate(self.vendor)
        self.assertEqual(len(self.api.get("/api/reviews/").data), 1)

    @patch("shop.functions.jsonplaceholder.requests.get")
    def test_external_filter_and_shape(self, get):
        get.return_value.json.return_value = [
            {"id": 1, "userId": 1, "title": "One", "body": "Text"},
            {"id": 2, "userId": 2, "title": "Two", "body": "Other"},
        ]
        self.assertEqual(
            get_posts(1),
            [{"id": 1, "title": "One", "body": "Text", "user_id": 1}],
        )
        self.assertEqual(get.call_args.kwargs["params"], {"userId": 1})

    @patch(
        "shop.functions.jsonplaceholder.requests.get",
        side_effect=requests.Timeout,
    )
    def test_external_failure(self, get):
        self.assertEqual(get_posts(), [])
        self.assertContains(
            self.client.get("/external-posts/"), "Posts could not be loaded"
        )

    @patch("shop.functions.jsonplaceholder.requests.get")
    def test_invalid_json(self, get):
        get.return_value.json.side_effect = ValueError("bad json")
        self.assertEqual(get_posts(), [])
