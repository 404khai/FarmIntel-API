from rest_framework import serializers
from .models import Organization, OrganizationMembership

class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "org_type", "description"]

    def create(self, validated_data):
        user = self.context["request"].user
        org = Organization.objects.create(created_by=user, **validated_data)
        # make the creator the owner
        OrganizationMembership.objects.create(
            organization=org,
            user=user,
            role="owner"
        )
        return org
