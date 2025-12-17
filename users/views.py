from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

from .serializers import (
    UserRegisterSerializer,
    LoginSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    UserProfileUpdateSerializer,
)
from emails.models import EmailOTP
from emails.services import EmailService


User = get_user_model()


# --------------------------------------------------------------------
# Utility: JWT Token Generator
# --------------------------------------------------------------------
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


# --------------------------------------------------------------------
# Register (Email + Password)
# --------------------------------------------------------------------
class RegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "User registered successfully. Verify your email to activate your account."},
            status=status.HTTP_201_CREATED,
        )


# --------------------------------------------------------------------
# Login (Email + Password)
# --------------------------------------------------------------------
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)
        return Response({
            "message": "Login successful",
            "tokens": tokens,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }, status=status.HTTP_200_OK)


# --------------------------------------------------------------------
# Request OTP (for password reset)
# --------------------------------------------------------------------
class RequestOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        purpose = request.data.get("purpose", "reset_password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        otp = EmailOTP.objects.create(
            user=user,
            code=uuid.uuid4().hex[:6].upper(),
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        # Send OTP via email service
        EmailService.send_otp_email(user, otp.code, purpose=purpose)
        return Response({"message": "OTP sent to your email."}, status=200)


# --------------------------------------------------------------------
# Verify OTP (for email verification)
# --------------------------------------------------------------------
class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        tokens = get_tokens_for_user(user)
        return Response(
            {"message": "Email verified successfully.", "tokens": tokens},
            status=status.HTTP_200_OK,
        )


# --------------------------------------------------------------------
# Reset Password with OTP
# --------------------------------------------------------------------
class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Password reset successfully."}, status=200)


# --------------------------------------------------------------------
# Google Authentication
# --------------------------------------------------------------------
class GoogleAuthView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"error": "id_token is required"}, status=400)

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
            email = idinfo.get("email")
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")
            picture = idinfo.get("picture", None)

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_verified": True,
                },
            )

            # If Google provides a profile picture, attach it once
            if picture and not user.profile_pic_url:
                user.profile_pic_url = picture
                user.save()

            tokens = get_tokens_for_user(user)
            return Response(
                {
                    "message": "Login successful via Google.",
                    "tokens": tokens,
                    "user": {"email": user.email, "name": user.full_name},
                },
                status=200,
            )
        except Exception as e:
            return Response({"error": "Invalid Google token", "details": str(e)}, status=400)


# --------------------------------------------------------------------
# Update User Profile
# --------------------------------------------------------------------
class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
