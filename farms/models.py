from django.db import models
from users.models import Farmer

# Create your models here.
class Crop(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name="crops")
    name = models.CharField(max_length=100)
    quantity = models.FloatField(default=0)  # in kg/tons etc
    image = models.ImageField(upload_to="crops/", blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.farmer.user.full_name}"
