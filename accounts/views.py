from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .models import User, LoginActivity
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    OTPVerifySerializer,
    LoginActivitySerializer,
)
from .utils import (
    generate_otp,
    send_otp_email,
    get_client_ip,
    get_location_from_ip,
)


# ----------------------------------------------------------------------------------
# REGISTER A NEW USER
# ----------------------------------------------------------------------------------
class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registered successfully!"})

        return Response(serializer.errors, status=400)


# ----------------------------------------------------------------------------------
# STEP-1 LOGIN (email + password) → send OTP
# ----------------------------------------------------------------------------------
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # user object returned from serializer
        user = serializer.validated_data['user']

        # Generate raw OTP
        otp = generate_otp()

        # Save OTP in user table
        user.otp = otp
        user.save()

        # Send OTP email
        send_otp_email(user.email, otp)

        return Response({"message": "OTP sent to your email."})
        

# ----------------------------------------------------------------------------------
# STEP-2 VERIFY OTP → login + save login history
# ----------------------------------------------------------------------------------
class VerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = serializer.validated_data["user"]

        # OTP Verified → Remove OTP
        user.otp = None
        user.save()

        # -------------------- JWT TOKEN GENERATION --------------------
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # -------------------- SAVE LOGIN ACTIVITY --------------------
        ip = get_client_ip(request)
        location = get_location_from_ip(ip)

        LoginActivity.objects.create(
            user=user,
            ip_address=ip,
            city=location.get["city"],
            region=location.get["region"],
            country=location.get["country"],
            latitude=location.get["latitude"],
            longitude=location.get["longitude"],
            device=request.META.get("HTTP_USER_AGENT"),
        )

        return Response({
            "message": "Login successful!",
            "access": access_token,
            "refresh": refresh_token
        })


# ----------------------------------------------------------------------------------
# LOGOUT USER
# ----------------------------------------------------------------------------------
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logged out successfully."})
        
        except Exception:
            return Response({"error": "Invalid token."}, status=400)
        


# ----------------------------------------------------------------------------------
# FETCH LOGIN HISTORY (IP + device + location)
# ----------------------------------------------------------------------------------
class LoginHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = LoginActivity.objects.filter(user=request.user).order_by("-created_at")
        serializer = LoginActivitySerializer(logs, many=True)
        return Response(serializer.data)
