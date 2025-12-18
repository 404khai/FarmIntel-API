from django.urls import path
from .views import FarmerAnalyticsView

urlpatterns = [
    path("farmer-stats", FarmerAnalyticsView.as_view(), name="farmer_analytics"),
]
