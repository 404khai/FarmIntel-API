from rest_framework import serializers
from .models import Cooperative, CooperativeMembership

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
    business_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = CooperativeMembership
        fields = [
            'id', 'profile_pic_url', 'full_name', 'member_id', 
            'role', 'role_display', 'location', 'business_name',
            'email', 'phone', 'status'
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
