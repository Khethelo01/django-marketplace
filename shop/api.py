from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Store, Review
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer


@api_view(["GET", "POST"])
def stores(request):
    if request.method == "GET":
        records = Store.objects.all()
        if request.query_params.get("vendor"):
            vendor = request.query_params["vendor"]
            if not vendor.isdecimal():
                return Response(
                    {"detail": "Vendor ID must be numeric."}, status=400
                )
            records = records.filter(vendor_id=vendor)
        return Response(StoreSerializer(records, many=True).data)
    if request.user.role != "vendor":
        return Response({"detail": "Vendors only."}, status=403)
    serializer = StoreSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(vendor=request.user)
    return Response(serializer.data, status=201)


@api_view(["GET", "POST"])
def products(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == "GET":
        return Response(
            ProductSerializer(store.products.all(), many=True).data
        )
    if request.user.role != "vendor" or store.vendor_id != request.user.pk:
        return Response(
            {"detail": "Only the store owner may add products."}, status=403
        )
    serializer = ProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(store=store)
    return Response(serializer.data, status=201)


@api_view(["GET"])
def reviews(request):
    if request.user.role != "vendor":
        return Response({"detail": "Vendors only."}, status=403)
    records = Review.objects.filter(product__store__vendor=request.user)
    return Response(ReviewSerializer(records, many=True).data)
