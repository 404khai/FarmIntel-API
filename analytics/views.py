from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import WeatherAnalyticsService

class FarmerAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Check if user has location data
        if not all([user.city, user.country]):
            return Response({
                "error": "Profile incomplete. Please set your city and country in your profile to view analytics."
            }, status=400)

        stats = WeatherAnalyticsService.get_farmer_analytics(user)
        
        if "error" in stats:
            return Response(stats, status=500)
            
        return Response(stats)
