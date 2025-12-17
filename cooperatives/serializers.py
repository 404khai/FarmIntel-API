from rest_framework import serializers
from .models import Cooperative, CooperativeMembership

class CooperativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooperative
        fields = ['id', 'name', 'description', 'image_url', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class CooperativeMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CooperativeMembership
        fields = ['id', 'user', 'cooperative', 'role', 'joined_at']
        read_only_fields = ['user', 'joined_at']
