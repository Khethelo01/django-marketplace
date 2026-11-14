"""Serializers for the Marketplace application."""

from rest_framework import serializers
from .models import Store, Product, Review


class StoreSerializer(serializers.ModelSerializer):
    """Storeserializer configuration and behaviour."""

    class Meta:
        """Configure model metadata or editable form fields."""

        model = Store
        fields = ["id", "vendor", "name", "description"]
        read_only_fields = ["vendor"]


class ProductSerializer(serializers.ModelSerializer):
    """Productserializer configuration and behaviour."""

    class Meta:
        """Configure model metadata or editable form fields."""

        model = Product
        fields = ["id", "store", "name", "description", "price", "stock"]
        read_only_fields = ["store"]


class ReviewSerializer(serializers.ModelSerializer):
    """Reviewserializer configuration and behaviour."""

    verified = serializers.BooleanField(read_only=True)

    class Meta:
        """Configure model metadata or editable form fields."""

        model = Review
        fields = ["id", "product", "buyer", "rating", "content", "verified"]
