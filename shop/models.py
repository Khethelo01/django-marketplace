"""Models for the Marketplace application."""

from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class User(AbstractUser):
    """Represent a registered buyer or vendor with a unique email."""

    role = models.CharField(
        max_length=10,
        choices=[("buyer", "Buyer"), ("vendor", "Vendor")],
        default="buyer",
    )
    email = models.EmailField(unique=True)


class Store(models.Model):
    """Represent a vendor-owned store and its catalogue identity."""

    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    def __str__(self):
        """Return a readable name for display and administration."""
        return self.name


class Product(models.Model):
    """Store product details, decimal price and available stock."""

    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        """Return a readable name for display and administration."""
        return self.name


class Order(models.Model):
    """Record a buyer checkout and its historical invoice total."""

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    invoice_sent = models.BooleanField(default=False)


class OrderItem(models.Model):
    """Preserve purchased quantities and historical unit prices."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


class Review(models.Model):
    """Record buyer feedback and derive purchase verification."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def verified(self):
        """Return whether this buyer has purchased the reviewed product."""
        return OrderItem.objects.filter(
            product=self.product, order__buyer=self.buyer
        ).exists()
