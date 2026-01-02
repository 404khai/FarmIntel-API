from rest_framework import serializers
from .models import Order, OrderTransaction
from crops.serializers import CropSerializer
from users.serializers import UserSerializer

class OrderSerializer(serializers.ModelSerializer):
    crop_details = CropSerializer(source='crop', read_only=True)
    buyer_details = UserSerializer(source='buyer', read_only=True)
    farmer_name = serializers.CharField(source='farmer.user.full_name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'buyer_details', 'farmer', 'farmer_name', 
            'crop', 'crop_details', 'cooperative', 'quantity', 
            'total_price', 'status', 'delivery_address', 'notes', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['buyer', 'farmer', 'status', 'total_price', 'created_at', 'updated_at']

    def validate(self, data):
        crop = data.get('crop')
        quantity = data.get('quantity')
        if crop and quantity:
            if quantity > crop.quantity_kg:
                raise serializers.ValidationError(f"Only {crop.quantity_kg}kg available.")
        return data

class OrderTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTransaction
        fields = '__all__'
