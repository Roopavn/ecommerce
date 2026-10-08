from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=200)
    def __str__(self): return self.name or self.email

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    digital = models.BooleanField(default=False)
    image = models.ImageField(upload_to="images", null=True, blank=True)
    @property
    def imageURL(self): return self.image.url if self.image else "/static/images/placeholder.png"
    def __str__(self): return self.name

class Order(models.Model):
    PAYMENT_PENDING = "pending"
    PAYMENT_PAID = "paid"
    PAYMENT_FAILED = "failed"
    PAYMENT_CHOICES = [(PAYMENT_PENDING,"Pending"),(PAYMENT_PAID,"Paid"),(PAYMENT_FAILED,"Failed")]
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_PENDING)
    payment_order_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    payment_notification_status = models.CharField(max_length=20, blank=True, default="")
    @property
    def get_cart_total(self): return sum(item.get_total for item in self.orderitem_set.select_related("product").all())
    @property
    def get_cart_items(self): return sum(item.quantity or 0 for item in self.orderitem_set.all())
    @property
    def shipping(self): return any(item.product and not item.product.digital for item in self.orderitem_set.select_related("product").all())
    def __str__(self): return str(self.id)

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    @property
    def get_total(self): return (self.product.price * self.quantity) if self.product else 0
    def __str__(self): return f"{self.product} x {self.quantity}"

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="India")
    date_added = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.address
