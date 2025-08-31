from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer, 
    CreateOrderSerializer, 
    UpdateOrderStatusSerializer
)
from shops.models import Shop, ShopCustomer
from products.models import Product

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request, shop_id):
    if request.user.role != 'CUSTOMER':
        return Response({
            'error': 'Only customers can place orders'
        }, status=status.HTTP_403_FORBIDDEN)
    
    shop = get_object_or_404(Shop, pk=shop_id)
    
    # Check if customer is linked to shop
    if not ShopCustomer.objects.filter(shop=shop, customer=request.user).exists():
        return Response({
            'error': 'You must be a customer of this shop to place orders'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CreateOrderSerializer(
        data=request.data, 
        context={'customer': request.user, 'shop': shop}
    )
    
    if serializer.is_valid():
        try:
            order = serializer.save()
            return Response(
                OrderSerializer(order).data, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    if request.user.role != 'CUSTOMER':
        return Response({
            'error': 'Only customers can view orders'
        }, status=status.HTTP_403_FORBIDDEN)
    
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    # Check permissions
    if request.user.role == 'CUSTOMER' and order.customer != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'SHOPKEEPER' and order.shop.owner != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shop_orders(request, shop_id):
    if request.user.role != 'SHOPKEEPER':
        return Response({
            'error': 'Only shopkeepers can view shop orders'
        }, status=status.HTTP_403_FORBIDDEN)
    
    shop = get_object_or_404(Shop, pk=shop_id)
    
    if shop.owner != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    orders = Order.objects.filter(shop=shop).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request, pk):
    if request.user.role != 'SHOPKEEPER':
        return Response({
            'error': 'Only shopkeepers can update order status'
        }, status=status.HTTP_403_FORBIDDEN)
    
    order = get_object_or_404(Order, pk=pk)
    
    if order.shop.owner != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = UpdateOrderStatusSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response(OrderSerializer(order).data)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)