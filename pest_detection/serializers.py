from rest_framework import serializers
from .models import PestDetection

class PestDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PestDetection
        fields = [
            "id",
            "image",
            "detected_pests",
            "confidence_scores",
            "tips",
            "created_at"
        ]
        read_only_fields = ["detected_pests", "confidence_scores", "tips"]
