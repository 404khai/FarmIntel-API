from rest_framework import serializers
from .models import B2BOrganization, B2BMembership, B2BOrganizationInvitation
from billing.models import Plan, Subscription, Transaction


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
    """Only show plans for org usage"""
    class Meta:
        model = Plan
        fields = "__all__"


class OrgSubscriptionSerializer(serializers.ModelSerializer):
    plan = OrgPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.filter(user_type="org"),
        source="plan",
        write_only=True
    )

    class Meta:
        model = Subscription
        fields = ["id", "user", "plan", "plan_id", "status", "start_date", "end_date"]
        read_only_fields = ["status", "start_date", "end_date"]
