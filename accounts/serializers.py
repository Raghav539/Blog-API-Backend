from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User,LoginActivity

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email','password','full_name']
        
    def create(self,validated_data):
        user = User(
            email=validated_data['email'],
            full_name=validated_data['full_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self,data):
        user=authenticate(email=data['email'],password=data['password'])
        if not user:
            raise serializers.ValidateError("Invalid email or password.")
        data['user']=user
        return data
    
    
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    
    def validate(self,data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("USer not found.")
        
        if user.otp != data['otp']:
            raise serializers.ValidationError("Invalid OTP.")
        
        data['user']=user
        return data
    
    
class LoginActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginActivity
        fields = '__all__'
        
        
        
        