from django.urls import path
from . import views
urlpatterns = [
 path("", views.store, name="store"), path("cart/", views.cart, name="cart"), path("checkout/", views.checkout, name="checkout"),
 path("create-payment-order/", views.create_payment_order, name="create_payment_order"), path("verify-payment/", views.verify_payment, name="verify_payment"),
 path("process_order/", views.process_order, name="process_order"), path("webhooks/razorpay/", views.razorpay_webhook, name="razorpay_webhook"),
]
