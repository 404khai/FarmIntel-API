from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Order, OrderTransaction
from .serializers import OrderSerializer, OrderTransactionSerializer
from crops.models import Crop
from billing.utils import initialize_transaction, verify_transaction
from emails.services import EmailService
from django.conf import settings
import uuid

class PlaceOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        crop = serializer.validated_data['crop']
        quantity = serializer.validated_data['quantity']
        total_price = crop.price_per_kg * quantity
        
        order = serializer.save(
            buyer=self.request.user,
            farmer=crop.farmer,
            total_price=total_price,
            status="PENDING"
        )
        
        # Send email to farmer
        EmailService.send_order_placed_email(order)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'farmer':
            return Order.objects.filter(farmer__user=user).order_by('-created_at')
        return Order.objects.filter(buyer=user).order_by('-created_at')

class OrderActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        """
        Action can be 'accept' or 'decline'.
        Only farmers can perform this.
        """
        order = get_object_or_404(Order, id=pk, farmer__user=request.user)
        action = request.data.get('action')

        if action == 'accept':
            order.status = 'ACCEPTED'
            order.save()
            EmailService.send_order_status_email(order, "accepted")
            return Response({"message": "Order accepted successfully."})
        elif action == 'decline':
            order.status = 'DECLINED'
            order.save()
            EmailService.send_order_status_email(order, "declined")
            return Response({"message": "Order declined."})
        
        return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

class InitializeOrderPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk, buyer=request.user)
        
        if order.status != 'ACCEPTED':
            return Response({"error": "Order must be accepted by farmer before payment."}, status=status.HTTP_400_BAD_REQUEST)

        # Use smallest unit (kobo for NGN)
        amount_kobo = int(order.total_price * 100)
        reference = f"ORD_{uuid.uuid4().hex[:12]}"
        
        # Create Transaction record
        OrderTransaction.objects.create(
            order=order,
            buyer=request.user,
            reference=reference,
            amount=order.total_price,
            status="INITIALIZED"
        )

        try:
            paystack_resp = initialize_transaction(
                email=request.user.email,
                amount_kobo=amount_kobo,
                callback_url=request.data.get('callback_url'),
                metadata={"order_id": order.id, "reference": reference}
            )
            return Response(paystack_resp)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from django.db import transaction as db_transaction
from transactions.models import Wallet, Transaction as FinancialTransaction

class VerifyOrderPaymentView(APIView):
    permission_classes = [permissions.AllowAny] # Paystack webhook or callback

    def post(self, request):
        reference = request.data.get('reference')
        if not reference:
            return Response({"error": "No reference provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification_resp = verify_transaction(reference)
            if verification_resp.get('data', {}).get('status') == 'success':
                with db_transaction.atomic():
                    tx = get_object_or_404(OrderTransaction, reference=reference)
                    if tx.status != "SUCCESS":
                        tx.status = "SUCCESS"
                        tx.paystack_response = verification_resp
                        tx.save()
                        
                        order = tx.order
                        order.status = "PAID"
                        order.save()
                        
                        # Update crop quantity
                        crop = order.crop
                        crop.quantity_kg -= order.quantity
                        crop.save()
                        
                        # Update farmer wallet and create financial transaction
                        farmer = order.farmer
                        wallet, _ = Wallet.objects.get_or_create(farmer=farmer)
                        wallet.balance += order.total_price
                        wallet.save()
                        
                        FinancialTransaction.objects.create(
                            user=order.buyer,
                            wallet=wallet,
                            amount=order.total_price,
                            reference=reference,
                            transaction_type="PAYMENT",
                            status="SUCCESS",
                            description=f"Payment for Order #{order.id}: {crop.name}",
                            metadata={"order_id": order.id}
                        )
                        
                        # Notify farmer of payment
                        EmailService.send_payment_success_email(order)
                
                return Response({"message": "Payment verified successfully."})
            else:
                return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
