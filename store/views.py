import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import Customer, Order, OrderItem, Product, ShippingAddress


def get_cart(request):
    try:
        cart = json.loads(request.COOKIES.get("cart", "{}"))
    except (TypeError, ValueError):
        cart = {}
    return cart if isinstance(cart, dict) else {}


def get_cart_data(request):
    cart = get_cart(request)
    product_ids = [int(pk) for pk in cart if str(pk).isdigit()]
    products = Product.objects.filter(id__in=product_ids)

    items = []
    cart_items = 0
    cart_total = 0

    for product in products:
        quantity = max(int(cart.get(str(product.id), {}).get("quantity", 0)), 0)
        if quantity:
            items.append({"product": product, "quantity": quantity, "total": product.price * quantity})
            cart_items += quantity
            cart_total += product.price * quantity

    return {
        "items": items,
        "cart_items": cart_items,
        "cart_total": cart_total,
    }


def store(request):
    products = Product.objects.all().order_by("id")
    cart = get_cart_data(request)
    return render(request, "store.html", {"products": products, **cart})


def cart(request):
    cart_data = get_cart_data(request)
    return render(request, "cart.html", cart_data)


def checkout(request):
    cart_data = get_cart_data(request)
    if not cart_data["items"]:
        return render(request, "cart.html", cart_data)
    return render(request, "checkout.html", cart_data)


@require_POST
def process_order(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    form_data = payload.get("form", {})
    shipping_data = payload.get("shipping", {})
    cart_data = get_cart_data(request)

    if not cart_data["items"]:
        return JsonResponse({"error": "Your cart is empty."}, status=400)

    email = (form_data.get("email") or "").strip()
    name = (form_data.get("name") or "").strip()

    if request.user.is_authenticated:
        customer, _ = Customer.objects.get_or_create(
            user=request.user,
            defaults={"name": request.user.get_full_name(), "email": request.user.email},
        )
        customer.name = customer.name or name or request.user.get_full_name()
        customer.email = customer.email or email or request.user.email
        customer.save(update_fields=["name", "email"])
    else:
        if not name or not email:
            return JsonResponse({"error": "Name and email are required."}, status=400)
        customer = Customer.objects.filter(user__isnull=True, email=email).first()
        if not customer:
            customer = Customer.objects.create(name=name, email=email)

    order = Order.objects.create(customer=customer)

    for item in cart_data["items"]:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["quantity"],
        )

    if any(not item["product"].digital for item in cart_data["items"]):
        required = ("address", "city", "state", "zipcode")
        if any(not str(shipping_data.get(field, "")).strip() for field in required):
            order.delete()
            return JsonResponse({"error": "Complete shipping information is required."}, status=400)

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=shipping_data.get("address", "").strip(),
            city=shipping_data.get("city", "").strip(),
            state=shipping_data.get("state", "").strip(),
            zipcode=shipping_data.get("zipcode", "").strip(),
            country=shipping_data.get("country", "India").strip() or "India",
        )

    order.complete = True
    order.transaction_id = payload.get("transaction_id") or f"ORDER-{order.id}"
    order.save(update_fields=["complete", "transaction_id"])

    return JsonResponse({"success": True, "order_id": order.id})
