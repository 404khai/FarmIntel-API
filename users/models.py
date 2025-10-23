# users/models.py

# apps/accounts/models.py
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

def generate_token():
    return uuid.uuid4().hex

class User(AbstractUser):
    """
    Email-first user model. Keep username optional if you used existing code.
    """
    firstName = models.CharField(max_length=150, blank=True, null=True)
    lastName = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    ROLE_FARMER = "FARMER"
    ROLE_COOP = "COOPERATIVE"
    ROLE_BUYER = "BUYER"
    ROLE_ADMIN = "ADMIN"
    ROLE_CHOICES = [
        (ROLE_FARMER, "Farmer"),
        (ROLE_COOP, "Cooperative"),
        (ROLE_BUYER, "Buyer"),
        (ROLE_ADMIN, "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_FARMER)
    is_verified = models.BooleanField(default=False)  # email verified
    phone = models.CharField(max_length=24, blank=True, null=True)

    USERNAME_FIELD = "email"


    def __str__(self):
        return self.email

# Lightweight farmer profile (optional fields)
class Farmer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="farmer")
    location = models.CharField(max_length=255, blank=True)
    crops = models.JSONField(default=list, blank=True)  # ["Maize","Rice"]
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farm_name or self.user.get_full_name() or self.user.email}"

# Lightweight buyer profile
class Buyer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buyer")
    company_name = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=255, blank=True)
    interested_crops = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name or self.user.email

# Simple OTP model for email verification or actions
class EmailOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    purpose = models.CharField(max_length=50, default="email_verification")  # e.g., 'signup', 'reset_password'

    def is_valid(self):
        return (not self.used) and (timezone.now() < self.expires_at)

    def mark_used(self):
        self.used = True
        self.save()


# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class User(AbstractUser):
#     class Role(models.TextChoices):
#         FARMER = "FARMER", "Farmer"
#         COOPERATIVE = "COOPERATIVE", "Cooperative"
#         BUYER = "BUYER", "Buyer"
#         ADMIN = "ADMIN", "Admin"

#     role = models.CharField(max_length=20, choices=Role.choices, default=Role.FARMER)
#     phone = models.CharField(max_length=20, blank=True, null=True)
#     is_verified = models.BooleanField(default=False)

#     # users/models.py
# class FarmerProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="farmer_profile")
#     farm_name = models.CharField(max_length=100)
#     location = models.CharField(max_length=150)
#     crops = models.JSONField(default=list)  # e.g., ["Maize", "Cassava"]
#     cooperative = models.ForeignKey("cooperatives.Cooperative", on_delete=models.SET_NULL, null=True, blank=True)

# class CooperativeProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cooperative_profile")
#     coop_name = models.CharField(max_length=150)
#     address = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     members = models.ManyToManyField(User, related_name="cooperative_members", blank=True)

# class BuyerProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="buyer_profile")
#     company_name = models.CharField(max_length=150)
#     location = models.CharField(max_length=150)
#     interested_crops = models.JSONField(default=list)
