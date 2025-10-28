from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    RequestOTPView,
    VerifyOTPView,
    ResetPasswordView,
    GoogleAuthView,
    UserProfileUpdateView,
)

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("request-otp", RequestOTPView.as_view(), name="request_otp"),
    path("verify-otp", VerifyOTPView.as_view(), name="verify_otp"),
    path("reset-password", ResetPasswordView.as_view(), name="reset_password"),
    path("google-auth", GoogleAuthView.as_view(), name="google_auth"),
    path("me", UserProfileUpdateView.as_view(), name="profile_update"),
]
