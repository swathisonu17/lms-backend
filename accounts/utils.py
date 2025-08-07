# accounts/utils.py (create this if not present)

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # secure encoding
    # 👇 Manually set your PC's IP here instead of using request.build_absolute_uri
    domain = ' 192.168.3.79'  # Replace with your actual PC IP
    verify_url = f"{domain}{reverse('verify-email', kwargs={'uidb64': uid, 'token': token})}"
    verify_url = request.build_absolute_uri(
        reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
    )

    subject = 'Verify Your LMS Account'
    message = f'Hi {user.username},\n\nClick the link to verify your email:\n{verify_url}'

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

