import random
from django.core.mail import send_mail
from django.conf import settings
import requests

#Generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email,otp):
    subject = "Your Login OTP"
    message = f"Your OTP for login is: {otp}\n\nValid for 5 minutes."
    send_mail(subject,message,settings.DEFAULT_FROM_EMAIL,[email])
    
    
def get_location_from_ip(ip):
    #Using ipapi.co
    try:
        url = f"https://ipapi.co/{ip}/json/"
        r = requests.get(url).json()
        
        return {
            "city": r.get("city"),
            "region": r.get("region"),
            "country": r.get("country_name"),
            "latitude": r.get("latitude"),
            "longitude": r.get("longitude"),
        }
    except:
        return {
            "city": None,
            "region": None,
            "country": None,
            "latitude": None,
            "longitude": None,
        }
        
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if x_forwarded_for:
        ip= x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#GET USER DEVICE / BROWSER INFO
def get_user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "Unknown Device")

# GET LOCATION USING IP
def get_location_from_ip(ip):
    try:
        url = f"https://ipapi.co/{ip}/json/"
        data = requests.get(url,timeout=3).json()
        return {
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country_name"),
        }
    except:
        return {
            "city": None,
            "region": None,
            "country": None,
        }
    
# GENERATE RAW OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# SEND OTP EMAIL
def send_otp_email(email, otp):
    subject = "Your Login OTP"
    message = f"Your OTP code is: {otp}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
