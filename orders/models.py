from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction
from users.models import User
from shops.models import Shop, ShopCustomer
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('DELIVERED', 'Delivered'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        super().clean()
        if self.customer and self.customer.role != 'CUSTOMER':
            raise ValidationError('Only customers can place orders')
        
        if self.customer and self.shop:
            if not ShopCustomer.objects.filter(shop=self.shop, customer=self.customer).exists():
                raise ValidationError('Customer must be linked to shop to place order')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def calculate_total(self):
        total = sum(item.quantity * item.price for item in self.order_items.all())
        self.total_amount = total
        self.save()
        return total
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} - {self.shop.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    def clean(self):
        super().clean()
        if self.quantity <= 0:
            raise ValidationError('Quantity must be greater than 0')
        
        if self.product and self.quantity > self.product.stock:
            raise ValidationError('Quantity cannot exceed available stock')
        
        if self.order and self.product:
            if self.product.shop != self.order.shop:
                raise ValidationError('Product must belong to the same shop as the order')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"