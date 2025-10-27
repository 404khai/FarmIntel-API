from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
from datetime import timedelta


def generate_token():
    return uuid.uuid4().hex[:6].upper()  # 6-digit OTP like "9F3B2D"


# --------------------------------------------------------------------
#  User Model
# --------------------------------------------------------------------
class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)

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
#  Email OTP Model
# --------------------------------------------------------------------
class EmailOTP(models.Model):
    PURPOSE_CHOICES = [
        ("email_verification", "Email Verification"),
        ("reset_password", "Reset Password"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    def mark_used(self):
        self.used = True
        self.save()


# --------------------------------------------------------------------
#  Farmer / Buyer Profiles
# --------------------------------------------------------------------
class Farmer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="farmer")
    location = models.CharField(max_length=255, blank=True)
    crops = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.full_name


class Buyer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buyer")
    company_name = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=255, blank=True)
    demanded_crops = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name or self.user.full_name


# --------------------------------------------------------------------
#  Organization (Co-op, B2B groups)
# --------------------------------------------------------------------
class Organization(models.Model):
    TYPE_CHOICES = [
        ("coop", "Cooperative"),
        ("b2b", "B2B Organization"),
    ]
    name = models.CharField(max_length=150)
    org_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_organizations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_org_type_display()})"


# --------------------------------------------------------------------
#  Membership (Farmer or Buyer member)
# --------------------------------------------------------------------
class OrganizationMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("farmer_member", "Farmer Member"),
        ("buyer_member", "Buyer Member"),
    ]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "user")

    def __str__(self):
        return f"{self.user.email} in {self.organization.name}"


# --------------------------------------------------------------------
#  Invitation Links
# --------------------------------------------------------------------
class OrganizationInvitation(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="invitations")
    invited_email = models.EmailField()
    role = models.CharField(max_length=20, choices=OrganizationMembership.ROLE_CHOICES)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=lambda: timezone.now() + timedelta(days=7))

    def is_valid(self):
        return not self.accepted and timezone.now() < self.expires_at
