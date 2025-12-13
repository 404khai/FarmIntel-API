from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid
from datetime import timedelta


def default_expiry():
    return timezone.now() + timedelta(days=7)


class B2BOrganization(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_b2b_organizations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (B2B Organization)"


class ApiKey(models.Model):
    organization = models.ForeignKey(B2BOrganization, on_delete=models.CASCADE, related_name="api_keys")
    key = models.CharField(max_length=64, unique=True)
    label = models.CharField(max_length=120, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization.name} -> {self.label or self.key[:8]}"


class B2BMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
    ]
    organization = models.ForeignKey(
        B2BOrganization,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="b2b_memberships"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "user")


class B2BOrganizationInvitation(models.Model):
    organization = models.ForeignKey(
        B2BOrganization,
        on_delete=models.CASCADE,
        related_name="invitations"
    )
    invited_email = models.EmailField()
    role = models.CharField(max_length=20, choices=B2BMembership.ROLE_CHOICES)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)

    def is_valid(self):
        return (not self.accepted) and timezone.now() < self.expires_at
