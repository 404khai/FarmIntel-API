from rest_framework import serializers
from .models import User, EmailOTP, Farmer, Buyer, Organization, OrganizationMembership, OrganizationInvitation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "is_verified"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        EmailOTP.create_otp(user, purpose="email_verification")
        return user


class EmailOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailOTP
        fields = ["code", "purpose", "expires_at", "used"]


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ["id", "organization", "user", "role", "joined_at"]


class OrganizationInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInvitation
        fields = "__all__"
