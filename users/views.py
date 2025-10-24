from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import User, EmailOTP, Organization, OrganizationMembership, OrganizationInvitation
from .serializers import *
from django.core.mail import send_mail


class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "Account created. OTP sent to email."}, status=201)

    @action(detail=False, methods=["post"])
    def verify_email(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        user = get_object_or_404(User, email=email)
        otp = EmailOTP.objects.filter(user=user, code=code, used=False).last()
        if otp and otp.is_valid():
            user.is_verified = True
            user.save()
            otp.mark_used()
            return Response({"message": "Email verified successfully."})
        return Response({"error": "Invalid or expired code."}, status=400)


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        org = serializer.save(created_by=self.request.user)
        OrganizationMembership.objects.create(
            organization=org, user=self.request.user, role="OWNER"
        )

    @action(detail=True, methods=["post"])
    def invite(self, request, pk=None):
        org = self.get_object()
        email = request.data.get("email")
        role = request.data.get("role", "FARMER_MEMBER")
        invite = OrganizationInvitation.objects.create(
            organization=org, invited_email=email, role=role
        )
        send_mail(
            subject=f"Invitation to join {org.name}",
            message=f"You have been invited to join {org.name}. Use token: {invite.token}",
            from_email="noreply@farmintel.com",
            recipient_list=[email],
        )
        return Response({"message": "Invitation sent."})


class InvitationAcceptViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def accept(self, request):
        token = request.data.get("token")
        email = request.data.get("email")
        invitation = get_object_or_404(OrganizationInvitation, token=token, invited_email=email)
        if not invitation.is_valid():
            return Response({"error": "Invalid or expired invitation."}, status=400)
        user = get_object_or_404(User, email=email)
        OrganizationMembership.objects.create(
            organization=invitation.organization, user=user, role=invitation.role
        )
        invitation.accepted = True
        invitation.save()
        return Response({"message": "Invitation accepted successfully."})
