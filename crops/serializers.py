from rest_framework import serializers
from .models import Crop


class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ["id", "image", "name", "variety", "quantity_kg", "harvest_date", "status", "price_per_kg", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

