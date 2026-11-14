"""Urls for the Marketplace application."""

from django.urls import path
from . import views, api

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("vendors/", views.vendors, name="vendors"),
    path(
        "vendors/<int:pk>/stores/", views.vendor_stores, name="vendor-stores"
    ),
    path("stores/", views.stores, name="stores"),
    path("products/", views.products, name="products"),
    path("reviews/", views.review_overview, name="reviews"),
    path("stores/new/", views.store_edit, name="store-create"),
    path("stores/<int:pk>/", views.store_detail, name="store"),
    path("stores/<int:pk>/edit/", views.store_edit, name="store-edit"),
    path(
        "stores/<int:store_pk>/products/new/",
        views.product_edit,
        name="product-create",
    ),
    path(
        "stores/<int:store_pk>/products/<int:pk>/edit/",
        views.product_edit,
        name="product-edit",
    ),
    path("delete/<str:kind>/<int:pk>/", views.delete, name="delete"),
    path("products/<int:pk>/", views.product_detail, name="product"),
    path("products/<int:pk>/review/", views.review, name="review"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart-add"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart-remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("invoices/<int:pk>/", views.invoice, name="invoice"),
    path("invoices/<int:pk>/send/", views.invoice_retry, name="invoice-retry"),
    path("api/stores/", api.stores, name="api-stores"),
    path("api/stores/<int:pk>/products/", api.products, name="api-products"),
    path("api/reviews/", api.reviews, name="api-reviews"),
    path("external-posts/", views.external_posts, name="external-posts"),
]
