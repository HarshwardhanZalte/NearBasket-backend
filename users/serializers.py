import random
import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User, OTP

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['mobile_number', 'name', 'email', 'address', 'profile_image_url', 'role']
    
    def validate_mobile_number(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Mobile number must be 10 digits")
        return value
    
    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long")
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'mobile_number', 'name', 'email', 'address', 'profile_image_url', 'role', 'created_at']
        read_only_fields = ['id', 'mobile_number', 'created_at']

class SendOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=10)
    
    def validate_mobile_number(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Mobile number must be 10 digits")
        return value

class VerifyOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=10)
    otp_code = serializers.CharField(max_length=6)
    
    def validate_mobile_number(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Mobile number must be 10 digits")
        return value