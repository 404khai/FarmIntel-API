from rest_framework import generics, permissions
from .models import Organization
from .serializers import OrganizationCreateSerializer

class OrganizationCreateView(generics.CreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()  # `user` is injected in serializer via context
