"""Services for the Marketplace application."""

import logging
from decimal import Decimal
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from .models import Order, OrderItem, Product

logger = logging.getLogger(__name__)


def create_order(buyer, cart):
    """Validate the cart and atomically save an order and reduce stock."""
    if not cart:
        raise ValueError("Your cart is empty.")
    with transaction.atomic():
        products = {
            str(p.pk): p
            for p in Product.objects.select_for_update().filter(pk__in=cart)
        }
        if set(products) != set(cart):
            raise ValueError("A product was removed. Please review your cart.")
        lines = []
        total = Decimal("0")
        for key, quantity in cart.items():
            product = products[key]
            if (
                type(quantity) is not int
                or quantity < 1
                or quantity > product.stock
            ):
                raise ValueError(f"Not enough stock for {product.name}.")
            lines.append((product, quantity))
            total += product.price * quantity
        order = Order.objects.create(buyer=buyer, total=total)
        for product, quantity in lines:
            changed = Product.objects.filter(
                pk=product.pk, stock__gte=quantity
            ).update(stock=F("stock") - quantity)
            if not changed:
                raise ValueError("Stock changed. Please retry checkout.")
            OrderItem.objects.create(
                order=order,
                product=product,
                name=product.name,
                quantity=quantity,
                unit_price=product.price,
            )
    return order


def send_invoice(order):
    """Email an invoice and record whether delivery succeeded."""
    body = f"Invoice #{order.pk}\n"
    for item in order.items.all():
        body += f"{item.name}: {item.quantity} x R{item.unit_price}\n"
    body += f"Total: R{order.total}"
    try:
        send_mail(
            f"Invoice #{order.pk}",
            body,
            None,
            [order.buyer.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Invoice delivery failed for order %s", order.pk)
        return False
    order.invoice_sent = True
    order.save(update_fields=["invoice_sent"])
    return True
