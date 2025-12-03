from django.urls import path
from .views import DiseaseDetectView

urlpatterns = [
    path("detect/", DiseaseDetectView.as_view(), name="detect-disease")
]
