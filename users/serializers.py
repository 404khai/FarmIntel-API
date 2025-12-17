from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import User, Farmer, Buyer
from emails.models import EmailOTP
from emails.services import EmailService
from organizations.models import B2BOrganization as Organization


# --------------------------------------------------------------------
#  Registration Serializer
# --------------------------------------------------------------------
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

        # Automatically create role-specific profile
        if role == "farmer":
            Farmer.objects.create(user=user)
        elif role == "buyer":
            Buyer.objects.create(user=user)
        elif role == "org":
            Organization.objects.create(
                name=f"{user.full_name or user.email}'s Organization",
                description="Auto-created organization profile",
                created_by=user,
            )

        # Generate OTP for email verification
        otp_code = uuid.uuid4().hex[:6].upper()
        EmailOTP.objects.create(
            user=user,
            code=otp_code,
            purpose="email_verification",
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        # Send welcome email
        EmailService.send_welcome_email(user)
        
        # Send OTP email for verification
        EmailService.send_otp_email(user, otp_code, purpose="email_verification")

        return user



# --------------------------------------------------------------------
#  Login Serializer
# --------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        # if not user.is_verified:
        #     raise serializers.ValidationError("Email not verified.")
        return {"user": user}


# --------------------------------------------------------------------
#  OTP Verification
# --------------------------------------------------------------------
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


# --------------------------------------------------------------------
#  Password Reset
# --------------------------------------------------------------------
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


# --------------------------------------------------------------------
#  Profile Update Serializer
# --------------------------------------------------------------------
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(required=False, allow_blank=True)
    crops = serializers.ListField(child=serializers.CharField(), required=False)
    company_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "profile_pic", "country", "state", "city", "farm_name", "crops", "company_name"]

    def update(self, instance, validated_data):
        # Extract role-specific data
        farm_name = validated_data.pop("farm_name", None)
        crops = validated_data.pop("crops", None)
        company_name = validated_data.pop("company_name", None)

        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update specialized profile
        if instance.role == "farmer":
            # Ensure farmer profile exists (it should, but safety first)
            farmer_profile, _ = Farmer.objects.get_or_create(user=instance)
            changed = False
            if farm_name is not None:
                farmer_profile.farm_name = farm_name
                changed = True
            if crops is not None:
                farmer_profile.crops = crops
                changed = True
            if changed:
                farmer_profile.save()

        elif instance.role == "buyer":
            buyer_profile, _ = Buyer.objects.get_or_create(user=instance)
            if company_name is not None:
                buyer_profile.company_name = company_name
                buyer_profile.save()

        return instance
