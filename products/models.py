from django.db import models
from django.core.exceptions import ValidationError
from shops.models import Shop

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    product_image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['shop', 'name']
    
    def clean(self):
        super().clean()
        if self.price <= 0:
            raise ValidationError('Price must be greater than 0')
        if self.stock < 0:
            raise ValidationError('Stock cannot be negative')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.shop.name}"