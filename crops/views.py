from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Crop
from .serializers import CropSerializer


class IsOwnerFarmer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return hasattr(request.user, "farmer") and obj.farmer.user_id == request.user.id

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "farmer")


class CropViewSet(viewsets.ModelViewSet):
    serializer_class = CropSerializer
    permission_classes = [IsOwnerFarmer]

    def get_queryset(self):
        return Crop.objects.filter(farmer__user=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        farmer = getattr(self.request.user, "farmer", None)
        serializer.save(farmer=farmer)

