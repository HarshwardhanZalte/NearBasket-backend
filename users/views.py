import random
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, OTP
from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer, 
    SendOTPSerializer, 
    VerifyOTPSerializer
)

def generate_otp():
    return str(random.randint(100000, 999999))

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # If serializer.save() returns a list, get the first user
        if isinstance(user, list):
            user_instance = user[0]
        else:
            user_instance = user
        return Response({
            'message': 'User registered successfully',
            'user_id': user_instance.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    serializer = SendOTPSerializer(data=request.data)
    if serializer.is_valid():
        if isinstance(serializer.validated_data, dict) and 'mobile_number' in serializer.validated_data:
            mobile_number = serializer.validated_data['mobile_number']
            
            try:
                user = User.objects.get(mobile_number=mobile_number)
            except User.DoesNotExist:
                return Response({
                    'error': 'User with this mobile number does not exist'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Generate and save OTP
            otp_code = generate_otp()
            OTP.objects.filter(user=user, is_verified=False).delete()  # Remove old unverified OTPs
            otp = OTP.objects.create(user=user, otp_code=otp_code)
            
            # In production, send SMS here
            print(f"OTP for {mobile_number}: {otp_code}")  # For development
            
            return Response({
                'message': 'OTP sent successfully',
                'otp': otp_code  # Remove this in production
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Mobile number not provided'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        if isinstance(serializer.validated_data, dict) and 'mobile_number' in serializer.validated_data and 'otp_code' in serializer.validated_data:
            mobile_number = serializer.validated_data['mobile_number']
            otp_code = serializer.validated_data['otp_code']
            
            try:
                user = User.objects.get(mobile_number=mobile_number)
                otp = OTP.objects.get(
                    user=user, 
                    otp_code=otp_code, 
                    is_verified=False,
                    created_at__gte=timezone.now() - timedelta(minutes=10)  # OTP valid for 10 minutes
                )
                
                # Mark OTP as verified
                otp.is_verified = True
                otp.save()
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'Login successful',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserProfileSerializer(user).data
                }, status=status.HTTP_200_OK)
                
            except (User.DoesNotExist, OTP.DoesNotExist):
                return Response({
                    'error': 'Invalid OTP or mobile number'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Mobile number or OTP code not provided'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)