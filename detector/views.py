from django.shortcuts import render

# detector/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ImageUploadSerializer
from .predictors.disease_predictor import model
from .services import TreatmentService

class DiseaseDetectView(APIView):

    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)

        if serializer.is_valid():
            image = serializer.validated_data["image"]

            predictions = model.predict(image)

            best = predictions[0]

            # confidence threshold
            if best["confidence"] < 0.60:
                return Response({
                    "status": "unsure",
                    "message": "The model is not fully certain. Here are possible matches:",
                    "candidates": predictions
                }, status=status.HTTP_200_OK)

            # Fetch AI Treatment Plan
            treatment = TreatmentService.get_treatment_plan(best["label"], best["confidence"])
            treatment_text = None
            if isinstance(treatment, dict):
                if treatment.get("status") == "success":
                    treatment_text = treatment.get("treatment_plan")
                else:
                    treatment_text = treatment.get("message")
            else:
                treatment_text = str(treatment)

            return Response({
                "status": "ok",
                "prediction": best,
                "treatment": treatment_text,
                "alternatives": predictions[1:]
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
