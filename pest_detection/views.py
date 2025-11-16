from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import PestDetection
from .serializers import PestDetectionSerializer
from .inference import run_pest_detection
from .pest_tips import PEST_TIPS


class PestDetectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if "image" not in request.FILES:
            return Response({"error": "Image is required"}, status=400)

        image = request.FILES["image"]

        # Save temp instance to get file path
        pest_instance = PestDetection.objects.create(
            user=request.user,
            image=image
        )

        # Run model inference
        detected_pests, confidence_scores = run_pest_detection(
            pest_instance.image.path
        )

        # Attach tips based on detected pests
        tips = []
        for pest in detected_pests:
            if pest.lower() in PEST_TIPS:
                tips.append({
                    "pest": pest,
                    "advice": PEST_TIPS[pest.lower()]
                })

        # Update instance
        pest_instance.detected_pests = detected_pests
        pest_instance.confidence_scores = confidence_scores
        pest_instance.tips = tips
        pest_instance.save()

        return Response(
            PestDetectionSerializer(pest_instance).data,
            status=201
        )

