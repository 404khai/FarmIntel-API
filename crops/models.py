from django.db import models
from django.conf import settings
from users.models import Farmer


class Crop(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name="farmer_crops")
    image_url = models.ImageField(upload_to="crop_images/", blank=True, null=True)
    name = models.CharField(max_length=150)
    variety = models.CharField(max_length=150, blank=True)
    quantity_kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    harvest_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default="available")
    price_per_kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.variety})"
