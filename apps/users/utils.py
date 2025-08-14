import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache 
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from twilio.rest import Client

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code, template_type='verification'):

    if template_type == 'verification':
        subject = 'Код підтвердження - AutoRia'
        template_name = 'emails/verification_code.html'
    else:
        subject = 'Скидання пароля - AutoRia'
        template_name = 'emails/password_reset.html'
    
    html_message = render_to_string(template_name, {
        'verification_code': code,
        'email': email
    })
    
    plain_message = strip_tags(html_message)
    
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=email_from,
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=html_message
        )
        print(f"DEBUG: Sent {template_type} email to {email} with code {code}")
    except Exception as e:
        print(f"ERROR: Failed to send {template_type} email to {email}: {e}")
        raise 

def send_verification_sms(phone_number, code):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    twilio_phone_number = settings.TWILIO_PHONE_NUMBER

    if not all([account_sid, auth_token, twilio_phone_number]):
        print("ERROR: Twilio credentials are not fully configured in settings.py")
        raise ValueError("Twilio credentials missing.")

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=f'Your verification code is: {code}',
            from_=twilio_phone_number,
            to=phone_number
        )
        print(f"DEBUG: Sent SMS to {phone_number} with SID: {message.sid}, code: {code}")
    except Exception as e:
        print(f"ERROR: Failed to send SMS to {phone_number}: {e}")
        raise

def store_verification_code(contact_info, code):
    cache.set(f'verification_code_{contact_info}', code, timeout=300)
    print(f"DEBUG: Stored code {code} for {contact_info} in cache.")

def get_verification_code(contact_info):
    code = cache.get(f'verification_code_{contact_info}')
    print(f"DEBUG: Retrieved code {code} for {contact_info} from cache.")
    return code

def delete_verification_code(contact_info):
    cache.delete(f'verification_code_{contact_info}')
    print(f"DEBUG: Deleted code for {contact_info} from cache.")