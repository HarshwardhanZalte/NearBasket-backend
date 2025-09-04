import random
import re
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import User, OTP

class ShopInfoSerializer(serializers.Serializer):
    """Serializer for shop information during shopkeeper registration"""
    name = serializers.CharField(max_length=100)
    address = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    shop_logo_url = serializers.URLField(required=False, allow_blank=True)
    
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Shop name cannot be empty")
        return value.strip()

class UserRegistrationSerializer(serializers.ModelSerializer):
    shop_info = ShopInfoSerializer(required=False, write_only=True)
    
    class Meta:
        model = User
        fields = ['mobile_number', 'name', 'email', 'address', 'profile_image_url', 'role', 'shop_info']
    
    def validate_mobile_number(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Mobile number must be 10 digits")
        return value
    
    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long")
        return value
    
    def validate(self, data):
        """Validate that shopkeepers provide shop information"""
        if data.get('role') == 'SHOPKEEPER':
            if not data.get('shop_info'):
                raise serializers.ValidationError({
                    'shop_info': 'Shop information is required for shopkeeper registration'
                })
            
            # Validate shop info
            shop_serializer = ShopInfoSerializer(data=data['shop_info'])
            if not shop_serializer.is_valid():
                raise serializers.ValidationError({
                    'shop_info': shop_serializer.errors
                })
        
        return data
    
    def create(self, validated_data):
        from shops.models import Shop  # Import here to avoid circular import
        
        shop_info = validated_data.pop('shop_info', None)
        
        with transaction.atomic():
            # Create user
            user = User.objects.create(**validated_data)
            
            # If shopkeeper, create shop
            if user.role == 'SHOPKEEPER' and shop_info:
                Shop.objects.create(
                    owner=user,
                    name=shop_info['name'],
                    address=shop_info['address'],
                    description=shop_info.get('description', ''),
                    shop_logo_url=shop_info.get('shop_logo_url', '')
                )
            
            return user

class UserProfileSerializer(serializers.ModelSerializer):
    shop = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'mobile_number', 'name', 'email', 'address', 'profile_image_url', 'role', 'created_at', 'shop']
        read_only_fields = ['id', 'mobile_number', 'created_at', 'role']
    
    def get_shop(self, obj):
        """Include shop information for shopkeepers"""
        if obj.role == 'SHOPKEEPER':
            try:
                shop = obj.shop
                return {
                    'id': shop.id,
                    'name': shop.name,
                    'address': shop.address,
                    'description': shop.description,
                    'shop_logo_url': shop.shop_logo_url,
                    'shop_id': shop.shop_id,
                    'created_at': shop.created_at
                }
            except:
                return None
        return None

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