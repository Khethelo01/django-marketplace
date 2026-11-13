from functools import wraps
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import RegisterForm, StoreForm, ProductForm, ReviewForm
from .models import Store, Product, Order
from .services import create_order, send_invoice


def role_required(role):
    def decorate(view):
        @login_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.user.role != role:
                return HttpResponseForbidden(
                    "This action is not available for your account role."
                )
            return view(request, *args, **kwargs)

        return wrapped

    return decorate


def home(request):
    return render(
        request,
        "shop/home.html",
        {
            "stores": Store.objects.all(),
            "products": Product.objects.select_related("store"),
        },
    )


def register(request):
    form = RegisterForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")
    return render(
        request, "form.html", {"form": form, "title": "Create an account"}
    )


@login_required
def dashboard(request):
    return render(
        request,
        "shop/dashboard.html",
        {
            "stores": Store.objects.filter(vendor=request.user),
            "orders": Order.objects.filter(buyer=request.user).order_by("-pk"),
        },
    )


def store_detail(request, pk):
    store = get_object_or_404(Store, pk=pk)
    return render(request, "shop/store.html", {"store": store})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(
        request,
        "shop/product.html",
        {"product": product, "form": ReviewForm()},
    )


@role_required("vendor")
def store_edit(request, pk=None):
    store = (
        get_object_or_404(Store, pk=pk, vendor=request.user) if pk else None
    )
    form = StoreForm(
        request.POST if request.method == "POST" else None, instance=store
    )
    if request.method == "POST" and form.is_valid():
        store = form.save(commit=False)
        store.vendor = request.user
        store.save()
        return redirect("dashboard")
    return render(
        request, "form.html", {"form": form, "title": "Manage store"}
    )


@role_required("vendor")
def product_edit(request, store_pk, pk=None):
    store = get_object_or_404(Store, pk=store_pk, vendor=request.user)
    product = get_object_or_404(Product, pk=pk, store=store) if pk else None
    form = ProductForm(
        request.POST if request.method == "POST" else None, instance=product
    )
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.store = store
        product.save()
        return redirect("dashboard")
    return render(
        request, "form.html", {"form": form, "title": "Manage product"}
    )


@role_required("vendor")
def delete(request, kind, pk):
    if kind == "store":
        obj = get_object_or_404(Store, pk=pk, vendor=request.user)
    elif kind == "product":
        obj = get_object_or_404(Product, pk=pk, store__vendor=request.user)
    else:
        from django.http import Http404

        raise Http404
    if request.method == "POST":
        obj.delete()
        return redirect("dashboard")
    return render(request, "delete.html", {"object": obj})


@role_required("buyer")
@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        quantity = int(request.POST.get("quantity", "1"))
        cart = request.session.get("cart", {})
        count = cart.get(str(pk), 0) + quantity
        if quantity < 1 or count > product.stock:
            raise ValueError
        cart[str(pk)] = count
        request.session["cart"] = cart
    except (ValueError, TypeError):
        messages.error(
            request, "Enter a positive quantity within available stock."
        )
    return redirect("cart")


@role_required("buyer")
@require_POST
def cart_remove(request, pk):
    cart = request.session.get("cart", {})
    cart.pop(str(pk), None)
    request.session["cart"] = cart
    return redirect("cart")


@role_required("buyer")
def cart(request):
    rows = []
    total = 0
    for key, quantity in request.session.get("cart", {}).items():
        product = Product.objects.filter(pk=key).first()
        if product:
            subtotal = product.price * quantity
            total += subtotal
            rows.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "subtotal": subtotal,
                }
            )
    return render(request, "shop/cart.html", {"rows": rows, "total": total})


@role_required("buyer")
@require_POST
def checkout(request):
    try:
        order = create_order(request.user, request.session.get("cart", {}))
    except ValueError as error:
        messages.error(request, str(error))
        return redirect("cart")
    request.session["cart"] = {}
    if not send_invoice(order):
        messages.warning(
            request,
            "Order saved, but email failed. You can retry from your invoice.",
        )
    return redirect("invoice", pk=order.pk)


@role_required("buyer")
def invoice(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    return render(request, "shop/invoice.html", {"order": order})


@role_required("buyer")
@require_POST
def invoice_retry(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    messages.info(
        request,
        "Invoice sent." if send_invoice(order) else "Email delivery failed.",
    )
    return redirect("invoice", pk=pk)


@role_required("buyer")
@require_POST
def review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ReviewForm(request.POST)
    if form.is_valid():
        record = form.save(commit=False)
        record.product = product
        record.buyer = request.user
        record.save()
        return redirect("product", pk=pk)
    return render(
        request,
        "form.html",
        {"form": form, "title": "Review product"},
        status=400,
    )


def external_posts(request):
    from .functions.jsonplaceholder import get_posts

    user_id = request.GET.get("user_id")
    if user_id and not user_id.isdecimal():
        return render(
            request,
            "external_posts.html",
            {"posts": [], "error": "Use a numeric user ID."},
        )
    return render(
        request, "external_posts.html", {"posts": get_posts(user_id or None)}
    )
