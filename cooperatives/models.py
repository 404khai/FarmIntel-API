# cooperatives/models.py
from django.db import models
from users.models import User

class Cooperative(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=150)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_cooperatives")
    members = models.ManyToManyField(User, related_name="joined_cooperatives", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class MembershipRequest(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="membership_requests")
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name="membership_requests")
    status = models.CharField(max_length=20, default="PENDING", choices=[("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")])
    requested_at = models.DateTimeField(auto_now_add=True)
