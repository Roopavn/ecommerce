import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import Order

logger = logging.getLogger(__name__)


def send_payment_notification(order, status):
    """Send one notification per payment status transition."""
    if not order.customer or not order.customer.email:
        return False
    if status not in {Order.PAYMENT_PAID, Order.PAYMENT_FAILED}:
        return False
    if order.payment_notification_status == status:
        return False

    if status == Order.PAYMENT_PAID:
        subject = f"Payment successful - Order #{order.id}"
        message = (
            f"Hi {order.customer.name or 'Customer'},\\n\\n"
            f"Your payment was successful.\\n\\n"
            f"Order: #{order.id}\\n"
            f"Payment ID: {order.payment_id or 'N/A'}\\n"
            f"Amount: INR {order.get_cart_total:.2f}\\n\\n"
            "Thank you for your purchase."
        )
    else:
        subject = f"Payment failed - Order #{order.id}"
        message = (
            f"Hi {order.customer.name or 'Customer'},\\n\\n"
            "Unfortunately, your payment could not be completed.\\n\\n"
            f"Order: #{order.id}\\n"
            f"Payment ID: {order.payment_id or 'N/A'}\\n\\n"
            "Please try the payment again."
        )

    try:
        sent = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.customer.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Unable to send payment notification for order %s", order.id)
        return False
    if sent:
        order.payment_notification_status = status
        order.save(update_fields=["payment_notification_status"])
    return bool(sent)
