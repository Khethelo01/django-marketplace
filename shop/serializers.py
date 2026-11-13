from rest_framework import serializers
from .models import Store, Product, Review


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "vendor", "name", "description"]
        read_only_fields = ["vendor"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "store", "name", "description", "price", "stock"]
        read_only_fields = ["store"]


class ReviewSerializer(serializers.ModelSerializer):
    verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "product", "buyer", "rating", "content", "verified"]
