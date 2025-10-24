
# apps/organizations/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid

class Organization(models.Model):
    """
    Generic organization table: cooperatives and B2B organizations (org_type).
    """
    TYPE_COOP = "COOP"
    TYPE_B2B = "B2B"
    ORG_TYPE_CHOICES = [
        (TYPE_COOP, "Cooperative"),
        (TYPE_B2B, "B2B Organization"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    org_type = models.CharField(max_length=10, choices=ORG_TYPE_CHOICES, default=TYPE_COOP)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="organizations_created")
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="joined_cooperatives", blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.org_type})"

class OrganizationMembership(models.Model):
    ROLE_OWNER = "OWNER"
    ROLE_MEMBER = "MEMBER"
    ROLE_BUYER = "BUYER_MEMBER"
    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_MEMBER, "Farmer Member"),
        (ROLE_BUYER, "Buyer"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "user")

    def __str__(self):
        return f"{self.user.email} -> {self.organization.name} as {self.role}"

class OrganizationInvitation(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_REJECTED = "REJECTED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="invitations")
    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="sent_invitations")
    invitee_email = models.EmailField()
    role = models.CharField(max_length=20, choices=OrganizationMembership.ROLE_CHOICES, default=OrganizationMembership.ROLE_MEMBER)
    token = models.CharField(max_length=64, unique=True, default=uuid.uuid4().hex)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # optional expiry

    def is_active(self):
        if self.status != self.STATUS_PENDING:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True

    def __str__(self):
        return f"Invite {self.invitee_email} to {self.organization.name} ({self.status})"
