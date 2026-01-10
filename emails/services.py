from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
import os
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service class for sending emails with HTML templates
    """
    
    @staticmethod
    def _attach_logo(email_message):
        """
        Attach the FarmIntel logo to the email message
        """
        logo_path = os.path.join(settings.BASE_DIR, 'emails', 'static', 'emails', 'logo.png')
        
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
                logo = MIMEImage(logo_data)
                logo.add_header('Content-ID', '<logo>')
                logo.add_header('Content-Disposition', 'inline', filename='logo.png')
                email_message.attach(logo)
        else:
            logger.warning(f"Logo file not found at {logo_path}")
    
    @staticmethod
    def send_welcome_email(user):
        """
        Send a welcome email to a newly registered user
        
        Args:
            user: User instance
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = "Welcome to FarmIntel! 🌱"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [user.email]
            
            # Context for the template
            context = {
                'user': user,
                'app_url': getattr(settings, 'APP_URL', 'https://farmintel.com'),
                'current_year': 2025,
            }
            
            # Render HTML content
            html_content = render_to_string('emails/welcome_email.html', context)
            
            # Create plain text version (fallback)
            text_content = strip_tags(html_content)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email
            )
            
            # Attach HTML version
            email.attach_alternative(html_content, "text/html")
            
            # Attach logo
            EmailService._attach_logo(email)
            
            # Send email
            email.send(fail_silently=False)
            
            logger.info(f"Welcome email sent successfully to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_otp_email(user, otp_code, purpose="email_verification"):
        """
        Send an OTP email to a user
        
        Args:
            user: User instance
            otp_code: The OTP code to send
            purpose: Purpose of the OTP (email_verification or reset_password)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Determine subject based on purpose
            if purpose == "reset_password":
                subject = "Reset Your FarmIntel Password"
                message = f"""
Hello {user.first_name or 'there'},

You requested to reset your password for your FarmIntel account.

Your password reset code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
The FarmIntel Team
                """
            else:
                subject = "Verify Your FarmIntel Email"
                message = f"""
Hello {user.first_name or 'there'},

Thank you for signing up with FarmIntel!

Your email verification code is: {otp_code}

This code will expire in 10 minutes.

If you didn't create this account, please ignore this email.

Best regards,
The FarmIntel Team
                """
            
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [user.email]
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=from_email,
                to=to_email
            )
            
            # Send email
            email.send(fail_silently=False)
            
            logger.info(f"OTP email ({purpose}) sent successfully to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {user.email}: {str(e)}")
            return False

    @staticmethod
    def send_order_placed_email(order):
        """Send notification to farmer when a new order is placed."""
        try:
            subject = f"New Order Received: {order.crop.name} 📦"
            context = {
                'order': order,
                'farmer': order.farmer.user,
                'app_url': getattr(settings, 'APP_URL', 'https://farmintel.com'),
                'current_year': 2025,
            }
            html_content = render_to_string('emails/order_placed_email.html', context)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[order.farmer.user.email]
            )
            email.attach_alternative(html_content, "text/html")
            EmailService._attach_logo(email)
            email.send(fail_silently=False)
            return True
        except Exception as e:
            logger.error(f"Failed to send order placed email: {str(e)}")
            return False

    @staticmethod
    def send_order_status_email(order, status_action):
        """Send notification to buyer when farmer accepts or declines an order."""
        try:
            subject = f"Your Order has been {status_action.capitalize()}! ✅" if status_action == 'accepted' else f"Your Order has been {status_action.capitalize()} ❌"
            context = {
                'order': order,
                'buyer': order.buyer,
                'status_action': status_action,
                'app_url': getattr(settings, 'APP_URL', 'https://farmintel.com'),
                'current_year': 2025,
            }
            html_content = render_to_string('emails/order_status_email.html', context)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[order.buyer.email]
            )
            email.attach_alternative(html_content, "text/html")
            EmailService._attach_logo(email)
            email.send(fail_silently=False)
            return True
        except Exception as e:
            logger.error(f"Failed to send order status email: {str(e)}")
            return False

    @staticmethod
    def send_payment_success_email(order):
        """Send notification to farmer and buyer when payment is successful."""
        try:
            # 1. Send Email to Farmer
            subject_farmer = f"Payment Received for Order #{order.id} 💰"
            context_farmer = {
                'order': order,
                'farmer': order.farmer.user,
                'app_url': getattr(settings, 'APP_URL', 'https://farmintel.com'),
                'current_year': 2025,
            }
            html_content_farmer = render_to_string('emails/payment_success_email.html', context_farmer)
            text_content_farmer = strip_tags(html_content_farmer)
            
            email_farmer = EmailMultiAlternatives(
                subject=subject_farmer,
                body=text_content_farmer,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[order.farmer.user.email]
            )
            email_farmer.attach_alternative(html_content_farmer, "text/html")
            EmailService._attach_logo(email_farmer)
            email_farmer.send(fail_silently=False)

            # 2. Send Email to Buyer
            subject_buyer = f"Payment Successful for Order #{order.id} 🎉"
            # Get transaction reference if possible (usually last transaction)
            reference = "N/A"
            if hasattr(order, 'transactions') and order.transactions.exists():
                reference = order.transactions.last().reference
                
            context_buyer = {
                'order': order,
                'buyer': order.buyer,
                'reference': reference,
                'app_url': getattr(settings, 'APP_URL', 'https://farmintel.com'),
                'current_year': 2025,
            }
            html_content_buyer = render_to_string('emails/payment_success_buyer_email.html', context_buyer)
            text_content_buyer = strip_tags(html_content_buyer)
            
            email_buyer = EmailMultiAlternatives(
                subject=subject_buyer,
                body=text_content_buyer,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[order.buyer.email]
            )
            email_buyer.attach_alternative(html_content_buyer, "text/html")
            EmailService._attach_logo(email_buyer)
            email_buyer.send(fail_silently=False)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send payment success emails: {str(e)}")
            # Don't fail the transaction if email fails, but log it.
            return False

    @staticmethod
    def send_out_of_stock_email(crop):
        """Send notification to farmer when crop goes out of stock."""
        try:
            subject = f"Stock Alert: {crop.name} is Sold Out! 📢"
            context = {
                'crop': crop,
                'farmer': crop.farmer.user,
                'app_url': getattr(settings, 'APP_URL', 'https://farmintel.com'),
                'current_year': 2025,
            }
            html_content = render_to_string('emails/out_of_stock_email.html', context)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[crop.farmer.user.email]
            )
            email.attach_alternative(html_content, "text/html")
            EmailService._attach_logo(email)
            email.send(fail_silently=False)
            return True
        except Exception as e:
            logger.error(f"Failed to send out of stock email: {str(e)}")
            return False
