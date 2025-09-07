from rest_framework import serializers
from .models import Shop, ShopCustomer
from users.models import User
from users.serializers import UserProfileSerializer

class ShopSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    
    class Meta:
        model = Shop
        fields = ['id', 'name', 'address', 'description', 'shop_logo_url', 
                 'shop_id', 'created_at', 'owner_name']
        read_only_fields = ['id', 'shop_id', 'created_at', 'owner_name']

class ShopUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating shop information (shopkeeper only)"""
    class Meta:
        model = Shop
        fields = ['name', 'address', 'description', 'shop_logo_url']
    
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Shop name cannot be empty")
        return value

class ShopCustomerSerializer(serializers.ModelSerializer):
    customer = UserProfileSerializer(read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    
    class Meta:
        model = ShopCustomer
        fields = ['id', 'customer', 'shop_name', 'joined_at']

class AddCustomerSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=10)
    
    def validate_mobile_number(self, value):
        import re
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Mobile number must be 10 digits")
        
        try:
            customer = User.objects.get(mobile_number=value)
            if customer.role != 'CUSTOMER':
                raise serializers.ValidationError("User is not a customer")
        except User.DoesNotExist:
            raise serializers.ValidationError("Customer with this mobile number does not exist")
        
        return value