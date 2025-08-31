import re
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    def create_user(self, mobile_number, name, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError('Mobile number is required')
        if not name:
            raise ValueError('Name is required')
        
        user = self.model(mobile_number=mobile_number, name=name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # For OTP-only users
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(mobile_number, name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('SHOPKEEPER', 'Shopkeeper'),
    ]
    
    mobile_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(r'^\d{10}$', 'Mobile number must be 10 digits')]
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['name']

    def clean(self):
        super().clean()
        if len(self.name) < 2:
            raise ValidationError('Name must be at least 2 characters long')
        
    def __str__(self):
        return f"{self.name} ({self.mobile_number})"

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"OTP for {self.user.mobile_number}"
