from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from .serializers import (
    EmailPasswordLoginSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
)
from .models import EmailOTP
from .utils import send_login_otp
from django.contrib.auth import get_user_model

User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class EmailPasswordLoginView(generics.GenericAPIView):
    serializer_class = EmailPasswordLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)
        return Response(tokens)


class RequestOTPView(generics.GenericAPIView):
    serializer_class = OTPRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data["email"])
        send_login_otp(user)
        return Response({"message": "OTP sent to your email."})


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = OTPVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)
        return Response(tokens)


class GoogleAuthView(generics.GenericAPIView):
    """
    Accepts an `id_token` from frontend Google login
    """
    def post(self, request):
        token = request.data.get("id_token")
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
            email = idinfo.get("email")
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")
            user, created = User.objects.get_or_create(email=email, defaults={
                "firstName": first_name,
                "lastName": last_name,
                "is_verified": True,
            })
            tokens = get_tokens_for_user(user)
            return Response(tokens)
        except Exception as e:
            return Response({"error": "Invalid Google token", "details": str(e)}, status=400)
