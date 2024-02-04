from django.core.mail import EmailMessage
from decouple import config
import time
import random
import hashlib

class Util:
    @staticmethod
    def send_email(data):
        email=EmailMessage(
            subject=data['subject'],
            body=data['body'],
            from_email=config('EMAIL_FROM'),
            to=[data['to_email']]
        )
        email.send()
        
    @staticmethod
    def generate_uid():
        timestamp = str(int(time.time() * 1000))  # Current timestamp in milliseconds
        random_part = str(random.randint(0, 999999))  # Random number for uniqueness

        # Combine timestamp and random part
        uid_string = timestamp + random_part

        # Hash the combined string to ensure uniqueness
        uid = hashlib.sha256(uid_string.encode()).hexdigest()

        return uid

    @staticmethod
    def generate_otp():
        return random.randint(100000, 999999)
