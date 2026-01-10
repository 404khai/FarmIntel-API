from rest_framework import generics, permissions
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer
from users.models import Farmer

class FarmerWalletView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        farmer, _ = Farmer.objects.get_or_create(user=self.request.user)
        wallet, _ = Wallet.objects.get_or_create(farmer=farmer)
        return wallet

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'farmer':
            farmer, _ = Farmer.objects.get_or_create(user=user)
            wallet, _ = Wallet.objects.get_or_create(farmer=farmer)
            return Transaction.objects.filter(wallet=wallet).order_by('-created_at')
        else:
            # See transactions they made
            return Transaction.objects.filter(user=user).order_by('-created_at')
