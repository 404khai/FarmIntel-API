from rest_framework import serializers
from .models import B2BOrganization, B2BMembership, B2BOrganizationInvitation
from .billing_models import OrgPlan, OrgSubscription, OrgTransaction


class B2BOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = B2BOrganization
        fields = ["id", "name", "description", "created_by", "created_at"]
        read_only_fields = ["created_by", "created_at"]


class B2BMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = B2BMembership
        fields = ["id", "user", "user_email", "role", "joined_at"]
        read_only_fields = ["joined_at"]


class B2BOrganizationInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = B2BOrganizationInvitation
        fields = ["id", "organization", "invited_email", "role", "token", "accepted", "created_at", "expires_at"]
        read_only_fields = ["token", "accepted", "created_at", "expires_at"]
        

class OrgPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgPlan
        fields = "__all__"


class OrgSubscriptionSerializer(serializers.ModelSerializer):
    plan = OrgPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=OrgPlan.objects.all(), source="plan", write_only=True
    )

    class Meta:
        model = OrgSubscription
        fields = ["id", "organization", "plan", "plan_id", "active", "start_date", "end_date"]
        read_only_fields = ["active", "start_date", "end_date"]
