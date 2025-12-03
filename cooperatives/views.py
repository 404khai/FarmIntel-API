from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cooperative, CooperativeMembership
from .serializers import CooperativeSerializer, CooperativeMembershipSerializer

class CooperativeViewSet(viewsets.ModelViewSet):
    queryset = Cooperative.objects.all()
    serializer_class = CooperativeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Create the cooperative
        cooperative = serializer.save(created_by=self.request.user)
        
        # Assign the creator as the owner
        CooperativeMembership.objects.create(
            user=self.request.user,
            cooperative=cooperative,
            role='owner'
        )

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        cooperative = self.get_object()
        user = request.user

        # Check if already a member
        if CooperativeMembership.objects.filter(user=user, cooperative=cooperative).exists():
            return Response({"detail": "You are already a member of this cooperative."}, status=status.HTTP_400_BAD_REQUEST)

        # Determine role based on user type
        role = None
        if user.role == 'farmer':
            role = 'member_farmer'
        elif user.role == 'buyer':
            role = 'member_buyer'
        else:
            return Response({"detail": "Only farmers and buyers can join cooperatives."}, status=status.HTTP_400_BAD_REQUEST)

        # Create membership
        membership = CooperativeMembership.objects.create(
            user=user,
            cooperative=cooperative,
            role=role
        )
        
        serializer = CooperativeMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
