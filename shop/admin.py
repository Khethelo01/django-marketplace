"""Admin for the Marketplace application."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Store, Product, Order, OrderItem, Review

admin.site.register(User, UserAdmin)
for model in [Store, Product, Order, OrderItem, Review]:
    admin.site.register(model)
