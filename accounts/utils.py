import random
from django.core.mail import send_mail
from django.conf import settings
import requests


# ------------------- OTP GENERATION -------------------
def generate_otp():
    return str(random.randint(100000, 999999))


# ------------------- SEND OTP EMAIL -------------------
def send_otp_email(email, otp):
    subject = "Your Login OTP"
    message = f"Your OTP for login is: {otp}\n\nValid for 5 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


# ------------------- GET CLIENT IP -------------------
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]

    return request.META.get("REMOTE_ADDR")


# ------------------- GET USER AGENT -------------------
def get_user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "Unknown Device")


# ------------------- GET LOCATION FROM IP -------------------
def get_location_from_ip(ip):
    try:
        url = f"https://ipapi.co/{ip}/json/"
        data = requests.get(url, timeout=3).json()

        return {
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country_name"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }

    except:
        return {
            "city": None,
            "region": None,
            "country": None,
            "latitude": None,
            "longitude": None,
        }
