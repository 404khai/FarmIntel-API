from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("system", "System"),
        ("coop", "Cooperative"),
        ("farmer", "Farmer"),
        ("buyer", "Buyer"),
        ("membership", "Membership"),
        ("ai", "AI Recommendation"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default="system")

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional: link notifications to cooperative or objects
    cooperative = models.ForeignKey(
        "cooperatives.Cooperative",
        on_delete=models.CASCADE,
        related_name="coop_notifications",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.title} -> {self.user.email}"
