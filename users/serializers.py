# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from .models import User, EmailOTP
from datetime import timedelta
import uuid

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=validated_data.get("role", "farmer"),
            password=validated_data["password"]
        )
        otp = EmailOTP.objects.create(
            user=user,
            code=uuid.uuid4().hex[:6].upper(),
            purpose="email_verification",
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        # TODO: Send OTP via email here
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_verified:
            raise serializers.ValidationError("Email not verified.")
        return {"user": user}


class EmailOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailOTP
        fields = ["code", "purpose"]


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=10)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        
        otp = EmailOTP.objects.filter(user=user, code=data["code"], used=False).last()
        if not otp or not otp.is_valid():
            raise serializers.ValidationError("Invalid or expired OTP.")
        
        otp.mark_used()
        user.is_verified = True
        user.save()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=10)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        
        otp = EmailOTP.objects.filter(
            user=user, code=data["code"], purpose="reset_password", used=False
        ).last()
        if not otp or not otp.is_valid():
            raise serializers.ValidationError("Invalid or expired OTP.")
        otp.mark_used()
        user.set_password(data["new_password"])
        user.save()
        return user
