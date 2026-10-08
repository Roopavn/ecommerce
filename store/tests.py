from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import Customer, Order, OrderItem, Product


class PaymentFlowTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Test Product", price=Decimal("100.00"))

    def add_cart(self, quantity=2):
        self.client.cookies["cart"] = f'{{"{self.product.id}": {{"quantity": {quantity}}}}}'

    @patch("store.views.razorpay_client")
    def test_create_payment_order_uses_server_side_price(self, mock_client):
        self.add_cart(2)
        mock_client.return_value.order.create.return_value = {
            "id": "order_test_123",
            "receipt": "ecom-test",
        }
        response = self.client.post(
            reverse("create_payment_order"),
            data='{"name":"Test User","email":"test@example.com"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        order = Order.objects.get(payment_order_id="order_test_123")
        self.assertEqual(order.payment_amount, Decimal("200.00"))
        self.assertEqual(OrderItem.objects.get(order=order).quantity, 2)

    def test_empty_cart_rejected(self):
        response = self.client.post(
            reverse("create_payment_order"),
            data='{"name":"Test User","email":"test@example.com"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_payment_notification_is_not_sent_twice(self):
        customer = Customer.objects.create(name="Test User", email="test@example.com")
        order = Order.objects.create(customer=customer, payment_amount=Decimal("100.00"))
        with patch("store.emails.send_mail", return_value=1) as send_mail:
            from .emails import send_payment_notification
            self.assertTrue(send_payment_notification(order, Order.PAYMENT_PAID))
            self.assertFalse(send_payment_notification(order, Order.PAYMENT_PAID))
            send_mail.assert_called_once()
