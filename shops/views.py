from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Shop, ShopCustomer
from .serializers import (
    ShopSerializer, 
    ShopCreateSerializer, 
    ShopCustomerSerializer, 
    AddCustomerSerializer,
)
from users.serializers import UserProfileSerializer
from users.models import User

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def shop_list_create(request):
    if request.method == 'GET':
        if request.user.role == 'SHOPKEEPER':
            shops = Shop.objects.filter(owner=request.user)
        else:
            # Customers see shops they've joined
            shop_customers = ShopCustomer.objects.filter(customer=request.user)
            shops = [sc.shop for sc in shop_customers]
        
        serializer = ShopSerializer(shops, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.role != 'SHOPKEEPER':
            return Response({
                'error': 'Only shopkeepers can create shops'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ShopCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            shop = serializer.save()
            return Response(ShopSerializer(shop).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def shop_detail(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    
    if request.method == 'GET':
        # Check if user has access to this shop
        if request.user.role == 'SHOPKEEPER' and shop.owner != request.user:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role == 'CUSTOMER':
            if not ShopCustomer.objects.filter(shop=shop, customer=request.user).exists():
                return Response({
                    'error': 'You are not a customer of this shop'
                }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ShopSerializer(shop)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if shop.owner != request.user:
            return Response({
                'error': 'Only shop owner can update shop'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ShopSerializer(shop, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if shop.owner != request.user:
            return Response({
                'error': 'Only shop owner can delete shop'
            }, status=status.HTTP_403_FORBIDDEN)
        
        shop.delete()
        return Response({
            'message': 'Shop deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_shop(request, pk):
    if request.user.role != 'CUSTOMER':
        return Response({
            'error': 'Only customers can join shops'
        }, status=status.HTTP_403_FORBIDDEN)
    
    shop = get_object_or_404(Shop, shop_id=pk)  # Use shop_id for joining
    
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
def add_customer(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    
    if shop.owner != request.user:
        return Response({
            'error': 'Only shop owner can add customers'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AddCustomerSerializer(data=request.data)
    if serializer.is_valid() and serializer.validated_data is not None:
        mobile_number = serializer.validated_data['mobile_number']
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
def shop_customers(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    
    if shop.owner != request.user:
        return Response({
            'error': 'Only shop owner can view customers'
        }, status=status.HTTP_403_FORBIDDEN)
    
    shop_customers = ShopCustomer.objects.filter(shop=shop)
    serializer = ShopCustomerSerializer(shop_customers, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_customer(request, pk, user_id):
    shop = get_object_or_404(Shop, pk=pk)
    
    if shop.owner != request.user:
        return Response({
            'error': 'Only shop owner can remove customers'
        }, status=status.HTTP_403_FORBIDDEN)
    
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
    if request.user.role != 'CUSTOMER':
        return Response({
            'error': 'Only customers can view joined shops'
        }, status=status.HTTP_403_FORBIDDEN)
    
    shop_customers = ShopCustomer.objects.filter(customer=request.user)
    shops = [sc.shop for sc in shop_customers]
    serializer = ShopSerializer(shops, many=True)
    return Response(serializer.data)