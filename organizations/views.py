from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
import uuid

from .models import B2BOrganization
from billing.models import Plan, Subscription, Transaction
from .serializers import OrgPlanSerializer, OrgSubscriptionSerializer


class OrgPlanListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        plans = Plan.objects.filter(user_type="org").order_by("tier")
        serializer = OrgPlanSerializer(plans, many=True)
        return Response(serializer.data)


#Initilizing paystack 
class InitializeOrgPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id):
        org = get_object_or_404(B2BOrganization, id=org_id)

        plan_id = request.data.get("plan_id")
        plan = get_object_or_404(Plan, id=plan_id, user_type="org")

        reference = uuid.uuid4().hex[:12]

        # Create a transaction for the org owner
        tx = Transaction.objects.create(
            user=org.created_by,
            reference=reference,
            amount=plan.price,
            metadata={"org_id": org.id, "plan_id": plan.id}
        )

        # Initialize payment through Paystack
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "email": org.created_by.email,
            "amount": plan.price,
            "metadata": tx.metadata
        }

        res = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=payload,
            headers=headers,
            timeout=30
        ).json()

        return Response({
            "authorization_url": res["data"]["authorization_url"],
            "reference": reference
        })


class OrgPaystackWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        event = request.data.get("event")
        data = request.data.get("data", {})

        if event == "charge.success":
            ref = data.get("reference")

            tx = Transaction.objects.get(reference=ref)
            tx.mark_success()

            org_id = data["metadata"]["org_id"]
            plan_id = data["metadata"]["plan_id"]

            org = B2BOrganization.objects.get(id=org_id)
            plan = Plan.objects.get(id=plan_id)

            # Create or update subscription for org owner
            sub, created = Subscription.objects.get_or_create(user=org.created_by)
            sub.plan = plan
            sub.activate()
            sub.paystack_reference = ref
            sub.save()

        return Response({"status": "ok"})
