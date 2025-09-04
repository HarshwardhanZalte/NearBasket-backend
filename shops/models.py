import uuid
from django.db import models
from django.core.exceptions import ValidationError
from users.models import User

def generate_shop_id():
    return str(uuid.uuid4())[:8].upper()

class Shop(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')  # Changed to OneToOneField
    name = models.CharField(max_length=100)
    address = models.TextField()
    description = models.TextField(blank=True, null=True)
    shop_logo_url = models.URLField(blank=True, null=True)
    shop_id = models.CharField(max_length=8, unique=True, default=generate_shop_id)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        super().clean()
        if self.owner and self.owner.role != 'SHOPKEEPER':
            raise ValidationError('Only shopkeepers can own shops')
        if not self.name.strip():
            raise ValidationError('Shop name cannot be empty')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.owner.name}"

class ShopCustomer(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop_customers')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='joined_shops')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['shop', 'customer']
    
    def clean(self):
        super().clean()
        if self.customer and self.customer.role != 'CUSTOMER':
            raise ValidationError('Only customers can join shops')
        if self.shop and self.customer and self.shop.owner == self.customer:
            raise ValidationError('Shopkeepers cannot join their own shop as customers')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.customer.name} - {self.shop.name}"