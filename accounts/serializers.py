from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, LoginActivity
from .utils import generate_otp


# ----------------------------------------------------------------------------------
# REGISTER SERIALIZER
# ----------------------------------------------------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    # password should not be readable, so write_only = True
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User   # our custom user model
        fields = ['email', 'full_name', 'password']

    def create(self, validated_data):
        """
        This method creates a new user.
        We NEVER store plain password; we must HASH it.
        """
        user = User(
            email=validated_data['email'],
            full_name=validated_data['full_name']
        )

        # Set hashed password (Django will encrypt it)
        user.set_password(validated_data['password'])

        user.save()
        return user


# ----------------------------------------------------------------------------------
# LOGIN SERIALIZER  (STEP-1: email + password)
# ----------------------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Authenticate user using Django's built-in authentication.
        Returns user object if credentials match.
        """
        user = authenticate(email=data['email'], password=data['password'])

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        # Return user object so views.py can use it
        data['user'] = user
        return data


# ----------------------------------------------------------------------------------
# OTP VERIFY SERIALIZER (STEP-2)
# ----------------------------------------------------------------------------------
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    def validate(self, data):
        """
        User enters email + OTP.
        We fetch user from email and check if OTP matches.
        """
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        # Compare stored OTP vs entered OTP
        if user.otp != data['otp']:
            raise serializers.ValidationError("Invalid OTP.")

        data['user'] = user
        return data
    
    def create_jwt_tokens(self,user):
        """
        Create JWT access and refresh tokens for the user.
        """
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


# ----------------------------------------------------------------------------------
# SERIALIZER FOR LOGIN ACTIVITY (history)
# ----------------------------------------------------------------------------------
class LoginActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginActivity
        fields = '__all__'
