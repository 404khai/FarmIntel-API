from django.db import models
from users.models import User

class Cooperative(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    image_url = models.ImageField(upload_to="coop_images/")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_cooperatives")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CooperativeMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("member_farmer", "Member Farmer"),
        ("member_buyer", "Member Buyer"),
        ("manager", "Manager"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coop_memberships")
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "cooperative")  # prevents duplicate membership

    def __str__(self):
        return f"{self.user.full_name} - {self.role} in {self.cooperative.name}"


class MembershipRequest(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="membership_requests")
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name="membership_requests")
    status = models.CharField(
        max_length=20,
        default="PENDING",
        choices=[("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")]
    )
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmer.full_name} requests {self.cooperative.name}"
