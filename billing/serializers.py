from rest_framework import serializers
from .models import Plan, Subscription, Transaction

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ["id", "name", "tier", "user_type", "price", "interval", "description"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "reference", "amount", "currency", "status", "metadata", "created_at", "verified_at"]
        read_only_fields = ["status", "created_at", "verified_at"]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.all(), source="plan", write_only=True
    )

    class Meta:
        model = Subscription
        fields = ["id", "user", "plan", "plan_id", "status", "start_date", "end_date", "paystack_reference"]
        read_only_fields = ["status", "start_date", "end_date", "paystack_reference", "user"]

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        plan = validated_data.get("plan")
        sub = Subscription.objects.create(user=user, plan=plan, status="inactive")
        return sub
