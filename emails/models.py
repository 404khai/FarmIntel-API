from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

# --------------------------------------------------------------------
#  Email OTP Model
# --------------------------------------------------------------------
class EmailOTP(models.Model):
    PURPOSE_CHOICES = [
        ("email_verification", "Email Verification"),
        ("reset_password", "Reset Password"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_otps")
    code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.code} ({self.purpose})"

    def is_valid(self):
        """Check if OTP is still valid (not expired and not used)"""
        return not self.used and timezone.now() < self.expires_at

    def mark_used(self):
        """Mark OTP as used"""
        self.used = True
        self.save()

