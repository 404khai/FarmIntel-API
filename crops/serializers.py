from rest_framework import serializers
from .models import Crop


class CropSerializer(serializers.ModelSerializer):
    # 'quantity_kg' and 'price_per_kg' are enforced as required.
    
    class Meta:
        model = Crop
        fields = ["id", "image_url", "name", "variety", "quantity_kg", "harvest_date", "status", "price_per_kg", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "quantity_kg": {"required": True},
            "price_per_kg": {"required": True},
        }


