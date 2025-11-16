from django.db import models
from django.conf import settings

class PestDetection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="pest_detections"
    )
    image = models.ImageField(upload_to="pest_detection/")
    detected_pests = models.JSONField(default=list, blank=True)
    confidence_scores = models.JSONField(default=list, blank=True)
    tips = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pest Detection by {self.user.email} at {self.created_at}"
