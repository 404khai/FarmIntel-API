from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
from datetime import timedelta


def generate_token():
    return uuid.uuid4().hex


# --------------------------------------------------------------------
#  User Model
# --------------------------------------------------------------------
class User(AbstractUser):
    username = None  # remove username
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    ROLE_FARMER = "FARMER"
    ROLE_BUYER = "BUYER"
    ROLE_ORG = "ORGANIZATION"
    ROLE_ADMIN = "ADMIN"
    ROLE_CHOICES = [
        (ROLE_FARMER, "Farmer"),
        (ROLE_BUYER, "Buyer"),
        (ROLE_ORG, "Organization"),
        (ROLE_ADMIN, "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_FARMER)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.email


# --------------------------------------------------------------------
#  OTP Model (email verification, login)
# --------------------------------------------------------------------
class EmailOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=50, default="email_verification")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    def mark_used(self):
        self.used = True
        self.save(update_fields=["used"])

    @classmethod
    def create_otp(cls, user, purpose="email_verification"):
        code = str(uuid.uuid4().int)[:6]
        return cls.objects.create(
            user=user,
            code=code,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=10),
        )


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
    interested_crops = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name or self.user.full_name


# --------------------------------------------------------------------
#  Organization (Co-op, B2B groups)
# --------------------------------------------------------------------
class Organization(models.Model):
    TYPE_CHOICES = [
        ("COOP", "Cooperative"),
        ("B2B", "B2B Organization"),
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
        ("OWNER", "Owner"),
        ("FARMER_MEMBER", "Farmer Member"),
        ("BUYER_MEMBER", "Buyer Member"),
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
