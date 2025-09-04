from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Shop, ShopCustomer
from .serializers import (
    ShopSerializer, 
    ShopUpdateSerializer,
    ShopCustomerSerializer, 
    AddCustomerSerializer,
    UserProfileSerializer
)
from users.models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_shop(request):
    """Get shopkeeper's shop or customer's joined shops"""
    if request.user.role == 'SHOPKEEPER':
        try:
            shop = request.user.shop
            serializer = ShopSerializer(shop)
            return Response(serializer.data)
        except Shop.DoesNotExist:
            return Response({
                'error': 'No shop found for this shopkeeper'
            }, status=status.HTTP_404_NOT_FOUND)
    
    elif request.user.role == 'CUSTOMER':
        # Return shops the customer has joined
        shop_customers = ShopCustomer.objects.filter(customer=request.user)
        shops = [sc.shop for sc in shop_customers]
        serializer = ShopSerializer(shops, many=True)
        return Response(serializer.data)
    
    return Response({
        'error': 'Invalid user role'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_my_shop(request):
    """Update shopkeeper's shop information"""
    if request.user.role != 'SHOPKEEPER':
        return Response({
            'error': 'Only shopkeepers can update shop information'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        return Response({
            'error': 'No shop found for this shopkeeper'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ShopUpdateSerializer(shop, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(ShopSerializer(shop).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shop_detail(request, shop_id):
    """Get shop details by shop_id (for customers to view before joining)"""
    shop = get_object_or_404(Shop, shop_id=shop_id)
    serializer = ShopSerializer(shop)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_shop(request, shop_id):
    """Customer joins a shop using shop_id"""
    if request.user.role != 'CUSTOMER':
        return Response({
            'error': 'Only customers can join shops'
        }, status=status.HTTP_403_FORBIDDEN)
    
    shop = get_object_or_404(Shop, shop_id=shop_id)
    
    if ShopCustomer.objects.filter(shop=shop, customer=request.user).exists():
        return Response({
            'error': 'You are already a customer of this shop'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    shop_customer = ShopCustomer.objects.create(shop=shop, customer=request.user)
    return Response({
        'message': 'Successfully joined shop',
        'shop': ShopSerializer(shop).data
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_customer(request):
    """Shopkeeper adds customer to their shop by mobile number"""
    if request.user.role != 'SHOPKEEPER':
        return Response({
            'error': 'Only shopkeepers can add customers'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        return Response({
            'error': 'No shop found for this shopkeeper'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = AddCustomerSerializer(data=request.data)
    if serializer.is_valid() and serializer.validated_data is not None:
        mobile_number = serializer.validated_data.get('mobile_number')
        if not mobile_number:
            return Response({
                'error': 'Mobile number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            customer = User.objects.get(mobile_number=mobile_number)
        except User.DoesNotExist:
            return Response({
                'error': 'Customer with this mobile number does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if ShopCustomer.objects.filter(shop=shop, customer=customer).exists():
            return Response({
                'error': 'Customer is already linked to this shop'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        shop_customer = ShopCustomer.objects.create(shop=shop, customer=customer)
        return Response({
            'message': 'Customer added successfully',
            'customer': UserProfileSerializer(customer).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shop_customers(request):
    """Get list of customers for shopkeeper's shop"""
    if request.user.role != 'SHOPKEEPER':
        return Response({
            'error': 'Only shopkeepers can view shop customers'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        return Response({
            'error': 'No shop found for this shopkeeper'
        }, status=status.HTTP_404_NOT_FOUND)
    
    shop_customers = ShopCustomer.objects.filter(shop=shop)
    serializer = ShopCustomerSerializer(shop_customers, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_customer(request, user_id):
    """Remove customer from shopkeeper's shop"""
    if request.user.role != 'SHOPKEEPER':
        return Response({
            'error': 'Only shopkeepers can remove customers'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        return Response({
            'error': 'No shop found for this shopkeeper'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        shop_customer = ShopCustomer.objects.get(shop=shop, customer_id=user_id)
        shop_customer.delete()
        return Response({
            'message': 'Customer removed successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    except ShopCustomer.DoesNotExist:
        return Response({
            'error': 'Customer not found in this shop'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_shops(request):
    """List shops a customer has joined"""
    if request.user.role != 'CUSTOMER':
        return Response({
            'error': 'Only customers can view joined shops'
        }, status=status.HTTP_403_FORBIDDEN)
    
    shop_customers = ShopCustomer.objects.filter(customer=request.user)
    shops = [sc.shop for sc in shop_customers]
    serializer = ShopSerializer(shops, many=True)
    return Response(serializer.data)