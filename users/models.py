from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
import uuid
from datetime import timedelta


def generate_token():
    return uuid.uuid4().hex[:6].upper()  # 6-digit OTP like "9F3B2D"


def default_expiry():
    return timezone.now() + timedelta(days=7)

# --------------------------------------------------------------------
#  User Model
# --------------------------------------------------------------------

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    country = models.CharField(max_length=120, blank=True, null=True)
    state = models.CharField(max_length=120, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)

    objects = UserManager()

    ROLE_CHOICES = [
        ('farmer', "Farmer"),
        ('buyer', "Buyer"),
        ('org', "Organization"),
        ('admin', "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='farmer')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.email



# --------------------------------------------------------------------
#  Farmer / Buyer Profiles
# --------------------------------------------------------------------
class Farmer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="farmer")
    farm_name = models.CharField(max_length=150, blank=True)
    crops = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.full_name


class Buyer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buyer")
    company_name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name or self.user.full_name



    



    
