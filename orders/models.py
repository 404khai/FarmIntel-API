from django.db import models
from django.conf import settings
from crops.models import Crop
from users.models import Farmer, Buyer
from cooperatives.models import Cooperative

class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("DECLINED", "Declined"),
        ("PAID", "Paid"),
        ("SHIPPED", "Shipped"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders_as_buyer")
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name="orders_as_farmer")
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="orders")
    cooperative = models.ForeignKey(Cooperative, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    
    delivery_address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.crop.name} by {self.buyer.email}"


class OrderTransaction(models.Model):
    STATUS_CHOICES = [
        ("INITIALIZED", "Initialized"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="INITIALIZED")
    paystack_response = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.reference} for Order #{self.order.id}"
