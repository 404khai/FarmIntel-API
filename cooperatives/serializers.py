from rest_framework import serializers
from .models import Cooperative, CooperativeMembership
from crops.models import Crop
from crops.serializers import CropSerializer

class CooperativeSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()

    class Meta:
        model = Cooperative
        fields = ['id', 'name', 'description', 'image_url', 'location', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']

    def get_location(self, obj):
        user = obj.created_by
        city = user.city or ""
        state = user.state or ""
        if city and state:
            return f"{city}, {state}"
        return city or state or "N/A"


class CooperativeMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CooperativeMembership
        fields = ['id', 'user', 'cooperative', 'role', 'joined_at']
        read_only_fields = ['user', 'joined_at']


class CooperativeMemberDetailSerializer(serializers.ModelSerializer):
    profile_pic_url = serializers.ImageField(source='user.profile_pic_url', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    member_id = serializers.CharField(source='user.member_id', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    location = serializers.SerializerMethodField()
    city = serializers.CharField(source='user.city', read_only=True)
    state = serializers.CharField(source='user.state', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    business_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    status = serializers.SerializerMethodField()
    crops = serializers.SerializerMethodField()

    class Meta:
        model = CooperativeMembership
        fields = [
            'id', 'profile_pic_url', 'full_name', 'member_id',
            'role', 'role_display', 'user_role', 'location', 'city', 'state', 'business_name',
            'email', 'phone', 'status', 'crops'
        ]

    def get_location(self, obj):
        user = obj.user
        city = user.city or ""
        state = user.state or ""
        if city and state:
            return f"{city}, {state}"
        return city or state or "N/A"

    def get_business_name(self, obj):
        user = obj.user
        if user.role == 'farmer':
            return getattr(user, 'farmer', None).farm_name if hasattr(user, 'farmer') else "N/A"
        elif user.role == 'buyer':
            return getattr(user, 'buyer', None).company_name if hasattr(user, 'buyer') else "N/A"
        return "N/A"

    def get_status(self, obj):
        return "Active" if obj.user.is_active else "Inactive"

    def get_crops(self, obj):
        user = obj.user
        if user.role == 'farmer':
            # Return actual inventory items so buyers can place orders
            crops = Crop.objects.filter(farmer__user=user)
            return CropSerializer(crops, many=True).data
        return []
