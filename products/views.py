from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer
from shops.models import Shop, ShopCustomer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_list_create(request, shop_id):
    shop = get_object_or_404(Shop, pk=shop_id)
    
    # Check access permissions
    if request.user.role == 'SHOPKEEPER':
        if shop.owner != request.user:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
    elif request.user.role == 'CUSTOMER':
        if not ShopCustomer.objects.filter(shop=shop, customer=request.user).exists():
            return Response({
                'error': 'You are not a customer of this shop'
            }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        products = Product.objects.filter(shop=shop)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.role != 'SHOPKEEPER':
            return Response({
                'error': 'Only shopkeepers can create products'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductCreateSerializer(data=request.data, context={'shop': shop})
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_detail(request, shop_id, pk):
    shop = get_object_or_404(Shop, pk=shop_id)
    product = get_object_or_404(Product, pk=pk, shop=shop)
    
    if request.method == 'GET':
        # Check access permissions
        if request.user.role == 'SHOPKEEPER':
            if shop.owner != request.user:
                return Response({
                    'error': 'Access denied'
                }, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role == 'CUSTOMER':
            if not ShopCustomer.objects.filter(shop=shop, customer=request.user).exists():
                return Response({
                    'error': 'You are not a customer of this shop'
                }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'DELETE']:
        if shop.owner != request.user:
            return Response({
                'error': 'Only shop owner can modify products'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            serializer = ProductSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            product.delete()
            return Response({
                'message': 'Product deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)