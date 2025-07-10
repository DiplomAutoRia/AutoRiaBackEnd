import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache 
from twilio.rest import Client

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code):
    subject = 'Your Verification Code'
    message = f'Your verification code is: {code}'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        print(f"DEBUG: Sent email to {email} with code {code}")
    except Exception as e:
        print(f"ERROR: Failed to send email to {email}: {e}")
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
            to=phone_number #У форматі E.164
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