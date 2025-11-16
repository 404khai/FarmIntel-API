from django.urls import path
from .views import PestDetectionView

urlpatterns = [
    path("detect/", PestDetectionView.as_view(), name="pest-detect"),
]
