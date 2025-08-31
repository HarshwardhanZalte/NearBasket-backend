from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'product_image_url', 
                 'description', 'created_at', 'shop_name']
        read_only_fields = ['id', 'created_at', 'shop_name']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'product_image_url', 'description']
    
    def create(self, validated_data):
        validated_data['shop'] = self.context['shop']
        return super().create(validated_data)