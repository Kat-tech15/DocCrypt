from django.core.mail import send_mail
from django.conf import settings 
from django.urls import reverse


class AccountEmailService:

    @staticmethod
    def send_activation_email(request, user, token):
        activation_path =reverse(
            "activation_account", kwargs={"token": token.token},
        )

        activation_url = request.build_absolute_uri(activation_path)

        subject = "Activate Your DocCrypt Student Account"
        message = f"""
Hello {user.first_name},
Your DocCrypt student account has been created successfully. 
Username / Admission Number: {user.username},

To activate your account and create your permanent password,
please use the link below:
{activation_url}

This activation link is valid for a limited period.
If you did not expect this email, please contact the system administrator.

Regards,
DocCrypt Administration
"""
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )