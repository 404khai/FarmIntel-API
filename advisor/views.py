from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import FarmDataSerializer
from .services.weather import fetch_daily_forecast
from .services.recommender import build_recommendations


class RecommendationView(APIView):
    def post(self, request):
        serializer = FarmDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        farm = serializer.validated_data
        loc = farm["location"]
        forecast = fetch_daily_forecast(loc["latitude"], loc["longitude"], days=14)
        recs = build_recommendations(farm, forecast)
        return Response({
            "status": "ok",
            "inputs": farm,
            "weather_source": "open-meteo",
            "forecast_days": len(forecast),
            "recommendations": recs,
        }, status=status.HTTP_200_OK)

