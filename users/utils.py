from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import EmailOTP
from .models import generate_token

def send_login_otp(user):
    otp_code = generate_token()
    expires = timezone.now() + timedelta(minutes=10)
    EmailOTP.objects.create(user=user, code=otp_code, purpose="login", expires_at=expires)
    send_mail(
        "Your Login OTP",
        f"Your login OTP is {otp_code}. It expires in 10 minutes.",
        "no-reply@farmintel.com",
        [user.email],
    )
    return otp_code
