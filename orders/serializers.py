from rest_framework import serializers
from .models import Order, OrderTransaction
from crops.serializers import CropSerializer
from users.serializers import UserSerializer

class OrderSerializer(serializers.ModelSerializer):
    crop_details = CropSerializer(source='crop', read_only=True)
    buyer_details = serializers.SerializerMethodField()
    farmer_details = serializers.SerializerMethodField()
    farmer_name = serializers.CharField(source='farmer.user.full_name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'buyer_details', 'farmer', 'farmer_name', 'farmer_details',
            'crop', 'crop_details', 'cooperative', 'quantity', 
            'total_price', 'status', 'delivery_address', 'notes', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['buyer', 'farmer', 'status', 'total_price', 'created_at', 'updated_at']

    def get_buyer_details(self, obj):
        buyer = obj.buyer
        return {
            "full_name": buyer.full_name,
            "profile_pic_url": buyer.profile_pic_url.url if buyer.profile_pic_url else None,
            "email": buyer.email,
            "phone": buyer.phone
        }

    def get_farmer_details(self, obj):
        farmer_profile = obj.farmer
        user = farmer_profile.user
        return {
            "full_name": user.full_name,
            "farm_name": farmer_profile.farm_name,
            "profile_pic_url": user.profile_pic_url.url if user.profile_pic_url else None,
            "email": user.email,
            "phone": user.phone,
            "city": user.city,
            "state": user.state
        }

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
