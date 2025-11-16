from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import B2BOrganization, B2BMembership, B2BOrganizationInvitation
from .billing_models import OrgPlan, OrgSubscription, OrgTransaction
from .serializers import (
    B2BOrganizationSerializer,
    B2BMembershipSerializer,
    B2BOrganizationInvitationSerializer,
    OrgPlanSerializer,
    OrgSubscriptionSerializer,
)
from django.conf import settings
import requests
import uuid


# ---------------------------------------------------------
# Create Organization
# ---------------------------------------------------------
class CreateB2BOrganizationView(generics.CreateAPIView):
    serializer_class = B2BOrganizationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        org = serializer.save(created_by=self.request.user)
        # owner automatically becomes a member
        B2BMembership.objects.create(
            organization=org,
            user=self.request.user,
            role="owner"
        )


# ---------------------------------------------------------
# List members
# ---------------------------------------------------------
class OrganizationMembersView(generics.ListAPIView):
    serializer_class = B2BMembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org_id = self.kwargs["org_id"]
        return B2BMembership.objects.filter(organization_id=org_id)


# ---------------------------------------------------------
# Invite member
# ---------------------------------------------------------
class InviteToOrganizationView(generics.CreateAPIView):
    serializer_class = B2BOrganizationInvitationSerializer
    permission_classes = [IsAuthenticated]


# ---------------------------------------------------------
# Accept invitation
# ---------------------------------------------------------
class AcceptInvitationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        invitation = get_object_or_404(B2BOrganizationInvitation, token=token)

        if not invitation.is_valid():
            return Response({"error": "Invitation expired or invalid"}, status=400)

        user = request.user
        B2BMembership.objects.create(
            organization=invitation.organization,
            user=user,
            role=invitation.role
        )
        invitation.accepted = True
        invitation.save()

        return Response({"message": "Invitation accepted"})


# ---------------------------------------------------------
# Billing: List Plans
# ---------------------------------------------------------
class OrgPlanListView(generics.ListAPIView):
    queryset = OrgPlan.objects.all()
    serializer_class = OrgPlanSerializer
    permission_classes = [AllowAny]


# ---------------------------------------------------------
# Initialize Payment
# ---------------------------------------------------------
class InitializeOrgPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id):
        organization = get_object_or_404(B2BOrganization, id=org_id)
        plan_id = request.data.get("plan_id")
        plan = get_object_or_404(OrgPlan, id=plan_id)

        reference = uuid.uuid4().hex[:12]
        amount = plan.price

        # Create transaction
        OrgTransaction.objects.create(
            organization=organization,
            reference=reference,
            amount=amount,
        )

        # Initialize via paystack
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "email": organization.created_by.email,
            "amount": amount,
            "metadata": {"org_id": organization.id, "plan_id": plan.id},
        }

        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers=headers,
            json=payload,
            timeout=30,
        )
        data = response.json()

        return Response({"authorization_url": data["data"]["authorization_url"]})


# ---------------------------------------------------------
# Payment Verification Webhook
# ---------------------------------------------------------
class OrgPaystackWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        event = request.data.get("event")
        data = request.data.get("data", {})

        if event == "charge.success":
            ref = data.get("reference")
            org_tx = get_object_or_404(OrgTransaction, reference=ref)

            org_id = data["metadata"]["org_id"]
            plan_id = data["metadata"]["plan_id"]

            organization = B2BOrganization.objects.get(id=org_id)
            plan = OrgPlan.objects.get(id=plan_id)

            # Create or update subscription
            sub, created = OrgSubscription.objects.get_or_create(organization=organization)
            sub.plan = plan
            sub.paystack_reference = ref
            sub.activate()

            org_tx.status = "success"
            org_tx.save()

        return Response({"status": "ok"})
