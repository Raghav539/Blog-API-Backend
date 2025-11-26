import os

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import LoginActivity
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    OTPVerifySerializer,
    LoginActivitySerializer,
    ProfileSerializer,
    changePasswordSerializer,
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
            city=location.get("city"),
            region=location.get("region"),
            country=location.get("country"),
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
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


class ProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)


class ProfileUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileImageUploadAPIView(APIView):
    """
    Upload or update the user's profile image only.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        image = request.FILES.get("profile_image")

        if not image:
            return Response({"error": "No image uploaded"}, status=400)

        user = request.user
        user.profile_image = image
        user.save()

        return Response({"message": "Profile image updated", "profile_image": user.profile_image.url})


class ProfileImageDeleteAPIView(APIView):
    """
    Deletes user's profile image.
    """
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        user = request.user

        if not user.profile_image:
            return Response({"error": "No profile image found"}, status=404)

        # Delete from storage
        if user.profile_image and os.path.isfile(user.profile_image.path):
            os.remove(user.profile_image.path)

        user.profile_image = None
        user.save()

        return Response({"message": "Profile image deleted successfully"})


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        serializer = changePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        # Check old password
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=400)

        # Update password
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password Updated Successfully"})
