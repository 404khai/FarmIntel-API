from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

USER_TYPE_CHOICES = [
    ("farmer", "Farmer"),
    ("buyer", "Buyer"),
    ("org", "Organization"),
]

SUBSCRIPTION_STATUS = [
    ("active", "Active"),
    ("trialing", "Trialing"),
    ("past_due", "Past Due"),
    ("canceled", "Canceled"),
    ("inactive", "Inactive"),
]


class Plan(models.Model):
    """
    Plans are simple: three tiers per user_type.
    price is in the smallest currency unit (kobo if NGN).
    """
    name = models.CharField(max_length=120)
    tier = models.PositiveSmallIntegerField()  # 1,2,3
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    price = models.PositiveIntegerField(help_text="Amount in kobo (e.g. 50000 for ₦500)")
    interval = models.CharField(
        max_length=10,
        choices=[("monthly", "Monthly"), ("yearly", "Yearly")],
        default="monthly",
    )
    description = models.TextField(blank=True)
    stripe_product_id = models.CharField(max_length=200, blank=True)  # future-proof placeholder

    class Meta:
        unique_together = ("tier", "user_type")

    def __str__(self):
        return f"{self.user_type} - {self.name} ({self.interval})"


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default="inactive")
    paystack_reference = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # optionally store paystack customer id for recurring charges or metadata
    paystack_customer = models.CharField(max_length=200, blank=True, null=True)

    def activate(self, paid_at=None):
        self.status = "active"
        self.start_date = paid_at or timezone.now()
        # set end_date based on plan.interval
        if self.plan.interval == "monthly":
            self.end_date = self.start_date + timedelta(days=30)
        else:
            self.end_date = self.start_date + timedelta(days=365)
        self.save()

    def cancel(self):
        self.status = "canceled"
        self.end_date = timezone.now()
        self.save()

    def is_active(self):
        return self.status == "active" and (self.end_date is None or self.end_date > timezone.now())

    def __str__(self):
        return f"{self.user.email} -> {self.plan} ({self.status})"


class Transaction(models.Model):
    """
    Store Paystack transactions (initialize -> verify)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="billing_transactions")
    reference = models.CharField(max_length=200, unique=True)
    amount = models.PositiveIntegerField()
    currency = models.CharField(max_length=10, default="NGN")
    status = models.CharField(max_length=50, default="initialized")  # initialized, success, failed
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def mark_success(self, verified_at=None):
        self.status = "success"
        self.verified_at = verified_at or timezone.now()
        self.save()

    def mark_failed(self):
        self.status = "failed"
        self.save()

    def __str__(self):
        return f"{self.reference} - {self.status}"
