# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        FARMER = "FARMER", "Farmer"
        COOPERATIVE = "COOPERATIVE", "Cooperative"
        BUYER = "BUYER", "Buyer"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.FARMER)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    # users/models.py
class FarmerProfile(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="farmer_profile")
        farm_name = models.CharField(max_length=100)
        location = models.CharField(max_length=150)
        crops = models.JSONField(default=list)  # e.g., ["Maize", "Cassava"]
        cooperative = models.ForeignKey("cooperatives.Cooperative", on_delete=models.SET_NULL, null=True, blank=True)

class CooperativeProfile(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cooperative_profile")
        coop_name = models.CharField(max_length=150)
        address = models.CharField(max_length=200)
        description = models.TextField(blank=True)
        members = models.ManyToManyField(User, related_name="cooperative_members", blank=True)

class BuyerProfile(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="buyer_profile")
        company_name = models.CharField(max_length=150)
        location = models.CharField(max_length=150)
        interested_crops = models.JSONField(default=list)
