from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import User, EmailOTP, Farmer, Buyer
from organizations.models import B2BOrganization, B2BMembership


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "role"]

    def create(self, validated_data):
        role = validated_data.get("role", "farmer")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role=role,
        )

        # Auto-create profile depending on role
        if role == "farmer":
            Farmer.objects.create(user=user)

        elif role == "buyer":
            Buyer.objects.create(user=user)

        elif role == "org":
            # Create a new B2B organization
            org = B2BOrganization.objects.create(
                name=f"{user.full_name or user.email}'s Organization",
                description="Auto-created B2B organization profile",
                created_by=user,
            )

            # Make user the owner
            B2BMembership.objects.create(
                organization=org,
                user=user,
                role="owner"
            )

        # Generate OTP for email verification
        EmailOTP.objects.create(
            user=user,
            code=uuid.uuid4().hex[:6].upper(),
            purpose="email_verification",
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        return user


