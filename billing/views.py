from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse

from .models import Plan, Subscription, Transaction
from .serializers import PlanSerializer, SubscriptionSerializer, TransactionSerializer
from . import utils as paystack_utils

import json
import hmac
import hashlib
from django.conf import settings

# -------------------------
# Plans List
# -------------------------
class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all().order_by("user_type", "tier")
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]


# -------------------------
# Create subscription locally (select plan) - creates Subscription instance
# -------------------------
class CreateSubscriptionView(generics.CreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# -------------------------
# Initialize Paystack transaction for a subscription
# -------------------------
class InitializePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Expects: { "subscription_id": <id>, "callback_url": optional }
        Returns: authorization_url (redirect user to Paystack)
        """
        subscription_id = request.data.get("subscription_id")
        callback_url = request.data.get("callback_url")
        subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)

        # amount is from plan.price (kobo)
        amount = subscription.plan.price

        # create a Transaction record with a unique reference (you can use uuid)
        import uuid
        reference = f"pay_{uuid.uuid4().hex[:12]}"

        tx = Transaction.objects.create(
            user=request.user,
            reference=reference,
            amount=amount,
            currency="NGN",
            status="initialized",
            metadata={"subscription_id": subscription.id},
        )

        # initialize with Paystack
        try:
            init_resp = paystack_utils.initialize_transaction(
                email=request.user.email,
                amount_kobo=amount,
                callback_url=callback_url,
                metadata={"subscription_id": subscription.id, "reference": reference}
            )
        except Exception as e:
            tx.mark_failed()
            return Response({"error": "Failed to initialize payment", "details": str(e)}, status=400)

        # Paystack returns data.authorization_url
        auth_url = init_resp.get("data", {}).get("authorization_url")
        paystack_ref = init_resp.get("data", {}).get("reference")
        # persist paystack reference if present
        if paystack_ref:
            tx.reference = paystack_ref
            tx.save()
            subscription.paystack_reference = paystack_ref
            subscription.save()

        return Response({"authorization_url": auth_url, "transaction_reference": tx.reference})


# -------------------------
# Webhook for Paystack (verify payment)
# -------------------------
@method_decorator(csrf_exempt, name="dispatch")
class PaystackWebhookView(APIView):
    permission_classes = [AllowAny]  # Paystack sends requests unauthenticated

    def post(self, request):
        # Verify signature (Paystack sends X-Paystack-Signature header)
        signature = request.META.get("HTTP_X_PAYSTACK_SIGNATURE", "")
        secret = getattr(settings, "PAYSTACK_SECRET_KEY", "")
        raw_body = request.body

        # Validate signature
        if secret:
            computed = hmac.new(secret.encode(), raw_body, hashlib.sha512).hexdigest()
            if not hmac.compare_digest(computed, signature):
                return HttpResponse(status=400)

        try:
            payload = json.loads(raw_body)
        except Exception:
            return HttpResponse(status=400)

        event = payload.get("event")
        data = payload.get("data", {})

        if event == "charge.success":
            reference = data.get("reference")
            # Mark transaction success
            try:
                tx = Transaction.objects.get(reference=reference)
            except Transaction.DoesNotExist:
                # possibly initialize with our reference mismatch; try metadata
                meta = data.get("metadata", {})
                # if no tx found, just exit
                return HttpResponse(status=404)

            tx.mark_success()
            # Activate subscription if metadata has subscription_id
            metadata = tx.metadata or {}
            sub_id = metadata.get("subscription_id") or data.get("metadata", {}).get("subscription_id")
            if sub_id:
                try:
                    sub = Subscription.objects.get(id=sub_id)
                    sub.activate()
                    sub.paystack_customer = data.get("customer", {}).get("id") or sub.paystack_customer
                    sub.paystack_reference = reference
                    sub.save()
                except Subscription.DoesNotExist:
                    pass

            return HttpResponse(status=200)

        # handle other events if needed
        return HttpResponse(status=200)


# -------------------------
# Subscription detail for user
# -------------------------
class SubscriptionDetailView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        sub_id = self.kwargs.get("pk")
        return get_object_or_404(Subscription, id=sub_id, user=self.request.user)


# -------------------------
# Cancel subscription (user)
# -------------------------
class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        sub = get_object_or_404(Subscription, id=pk, user=request.user)
        sub.cancel()
        return Response({"message": "Subscription cancelled"}, status=200)
