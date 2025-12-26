from rest_framework import generics, permissions
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer

class FarmerWalletView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(farmer__user=self.request.user)
        return wallet

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'farmer':
            # See transactions related to their wallet
            wallet, _ = Wallet.objects.get_or_create(farmer__user=user)
            return Transaction.objects.filter(wallet=wallet).order_by('-created_at')
        else:
            # See transactions they made
            return Transaction.objects.filter(user=user).order_by('-created_at')
