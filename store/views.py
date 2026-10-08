import json
import os
import uuid
from decimal import Decimal

import razorpay
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .emails import send_payment_notification
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
    items, cart_items, cart_total = [], 0, Decimal("0.00")
    for product in products:
        quantity = max(int(cart.get(str(product.id), {}).get("quantity", 0)), 0)
        if quantity:
            total = product.price * quantity
            items.append({"product": product, "quantity": quantity, "total": total})
            cart_items += quantity
            cart_total += total
    return {"items": items, "cart_items": cart_items, "cart_total": cart_total}


def razorpay_client():
    key_id = os.environ.get("RAZORPAY_KEY_ID")
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        raise RuntimeError("Razorpay credentials are not configured.")
    return razorpay.Client(auth=(key_id, key_secret))


def store(request):
    products = Product.objects.all().order_by("id")
    return render(request, "store.html", {"products": products, **get_cart_data(request)})


def cart(request):
    return render(request, "cart.html", get_cart_data(request))


def checkout(request):
    data = get_cart_data(request)
    if not data["items"]:
        return render(request, "cart.html", data)
    return render(request, "checkout.html", data)


@require_POST
def create_payment_order(request):
    data = get_cart_data(request)
    if not data["items"]:
        return JsonResponse({"error": "Your cart is empty."}, status=400)

    try:
        request_data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    name = (request_data.get("name") or "").strip()
    email = (request_data.get("email") or "").strip()
    if not name or not email:
        return JsonResponse({"error": "Name and email are required."}, status=400)

    customer = Customer.objects.filter(user=request.user).first() if request.user.is_authenticated else Customer.objects.filter(user__isnull=True, email=email).first()
    if not customer:
        customer = Customer.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
        )
    else:
        customer.name = name
        customer.email = email
        customer.save(update_fields=["name", "email"])

    amount_paise = int(data["cart_total"] * 100)
    order = Order.objects.create(customer=customer)
    for item in data["items"]:
        OrderItem.objects.create(order=order, product=item["product"], quantity=item["quantity"])

    rp_order = razorpay_client().order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"ecom-{order.id}-{uuid.uuid4().hex[:8]}",
        "payment_capture": 1,
    })
    order.payment_order_id = rp_order["id"]
    order.transaction_id = rp_order["receipt"]
    order.save(update_fields=["payment_order_id", "transaction_id"])
    return JsonResponse({
        "key": os.environ["RAZORPAY_KEY_ID"],
        "amount": amount_paise,
        "currency": "INR",
        "razorpay_order_id": rp_order["id"],
        "order_id": order.id,
    })


@require_POST
def verify_payment(request):
    try:
        data = json.loads(request.body or "{}")
        params = {
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"],
        }
    except (KeyError, json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid payment verification payload."}, status=400)

    order = Order.objects.filter(payment_order_id=params["razorpay_order_id"]).first()
    if not order:
        return JsonResponse({"error": "Order not found."}, status=404)

    try:
        razorpay_client().utility.verify_payment_signature(params)
    except razorpay.errors.SignatureVerificationError:
        order.payment_status = Order.PAYMENT_FAILED
        order.save(update_fields=["payment_status"])
        send_payment_notification(order, Order.PAYMENT_FAILED)
        return JsonResponse({"error": "Payment signature verification failed."}, status=400)

    order.payment_id = params["razorpay_payment_id"]
    order.payment_status = Order.PAYMENT_PAID
    order.complete = True
    order.save(update_fields=["payment_id", "payment_status", "complete"])
    send_payment_notification(order, Order.PAYMENT_PAID)
    return JsonResponse({"success": True, "order_id": order.id})


@csrf_exempt
@require_POST
def razorpay_webhook(request):
    secret = os.environ.get("RAZORPAY_WEBHOOK_SECRET")
    signature = request.headers.get("X-Razorpay-Signature")
    if not secret or not signature:
        return JsonResponse({"error": "Webhook configuration/signature missing."}, status=400)
    try:
        razorpay_client().utility.verify_webhook_signature(request.body, signature, secret)
        payload = json.loads(request.body)
    except (razorpay.errors.SignatureVerificationError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid webhook."}, status=400)

    event = payload.get("event")
    payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
    rp_order_id = payment.get("order_id")
    order = Order.objects.filter(payment_order_id=rp_order_id).first()
    if order:
        if event in {"payment.captured", "order.paid"}:
            order.payment_id = payment.get("id") or order.payment_id
            order.payment_status = Order.PAYMENT_PAID
            order.complete = True
            order.save(update_fields=["payment_id", "payment_status", "complete"])
            send_payment_notification(order, Order.PAYMENT_PAID)
        elif event == "payment.failed":
            order.payment_id = payment.get("id") or order.payment_id
            order.payment_status = Order.PAYMENT_FAILED
            order.complete = False
            order.save(update_fields=["payment_id", "payment_status", "complete"])
            send_payment_notification(order, Order.PAYMENT_FAILED)
    return JsonResponse({"received": True})


@require_POST
def process_order(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    data = get_cart_data(request)
    payment_id, rp_order_id = payload.get("razorpay_payment_id"), payload.get("razorpay_order_id")
    if not data["items"]:
        return JsonResponse({"error": "Your cart is empty."}, status=400)

    order = Order.objects.filter(payment_order_id=rp_order_id, payment_id=payment_id, payment_status=Order.PAYMENT_PAID).first()
    if not order:
        return JsonResponse({"error": "Payment is not verified."}, status=400)

    form, shipping = payload.get("form", {}), payload.get("shipping", {})
    name, email = (form.get("name") or "").strip(), (form.get("email") or "").strip()
    if not name or not email:
        return JsonResponse({"error": "Name and email are required."}, status=400)

    customer = Customer.objects.filter(user=request.user).first() if request.user.is_authenticated else Customer.objects.filter(user__isnull=True, email=email).first()
    if not customer:
        customer = Customer.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
        )

    with transaction.atomic():
        order.customer = customer
        for item in data["items"]:
            OrderItem.objects.get_or_create(order=order, product=item["product"], defaults={"quantity": item["quantity"]})
        if any(not item["product"].digital for item in data["items"]):
            required = ("address", "city", "state", "zipcode")
            if any(not str(shipping.get(field, "")).strip() for field in required):
                return JsonResponse({"error": "Complete shipping information is required."}, status=400)
            ShippingAddress.objects.get_or_create(
                order=order,
                defaults={
                    "customer": customer,
                    "address": shipping["address"].strip(),
                    "city": shipping["city"].strip(),
                    "state": shipping["state"].strip(),
                    "zipcode": shipping["zipcode"].strip(),
                    "country": shipping.get("country", "India").strip() or "India",
                },
            )
        order.save(update_fields=["customer"])
    return JsonResponse({"success": True, "order_id": order.id})
