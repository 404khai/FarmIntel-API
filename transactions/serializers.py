from rest_framework import serializers
from .models import Wallet, Transaction

class WalletSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.user.full_name', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'farmer', 'farmer_name', 'balance', 'updated_at']
        read_only_fields = ['balance', 'farmer']

class TransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'user_email', 'wallet', 'amount', 
            'reference', 'transaction_type', 'status', 
            'description', 'metadata', 'created_at'
        ]
        read_only_fields = ['reference', 'status', 'user']
