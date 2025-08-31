from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from products.models import Product
from users.serializers import UserProfileSerializer
from shops.serializers import ShopSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']
        read_only_fields = ['id', 'price', 'product_name']

class OrderSerializer(serializers.ModelSerializer):
    customer = UserProfileSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'shop', 'status', 'total_amount', 
                 'created_at', 'updated_at', 'order_items']
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']

class CreateOrderSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        min_length=1
    )
    
    def validate_items(self, value):
        for item in value:
            if 'product_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError(
                    "Each item must have 'product_id' and 'quantity'"
                )
            
            try:
                quantity = int(item['quantity'])
                if quantity <= 0:
                    raise serializers.ValidationError("Quantity must be greater than 0")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Quantity must be a valid integer")
        
        return value
    
    def create(self, validated_data):
        customer = self.context['customer']
        shop = self.context['shop']
        
        with transaction.atomic():
            # Create order
            order = Order.objects.create(customer=customer, shop=shop)
            
            # Create order items
            for item_data in validated_data['items']:
                product = Product.objects.get(
                    id=item_data['product_id'], 
                    shop=shop
                )
                quantity = int(item_data['quantity'])
                
                if quantity > product.stock:
                    raise serializers.ValidationError(
                        f"Not enough stock for {product.name}. Available: {product.stock}"
                    )
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
            
            # Calculate total
            order.calculate_total()
            
        return order

class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
    
    def validate_status(self, value):
        if self.instance and self.instance.status in ['DELIVERED', 'REJECTED']:
            raise serializers.ValidationError(
                "Cannot modify order that is already delivered or rejected"
            )
        return value
    
    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status', instance.status)
        
        # If order is being accepted, reduce product stock
        if old_status == 'PENDING' and new_status == 'ACCEPTED':
            with transaction.atomic():
                for item in instance.order_items.all():
                    product = item.product
                    if product.stock < item.quantity:
                        raise serializers.ValidationError(
                            f"Not enough stock for {product.name}"
                        )
                    product.stock -= item.quantity
                    product.save()
        
        # If order is being rejected after acceptance, restore stock
        elif old_status == 'ACCEPTED' and new_status == 'REJECTED':
            with transaction.atomic():
                for item in instance.order_items.all():
                    product = item.product
                    product.stock += item.quantity
                    product.save()
        
        instance.status = new_status
        instance.save()
        return instance