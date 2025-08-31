from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'shop', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at', 'shop']
    search_fields = ['customer__name', 'shop__name']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__created_at']
    search_fields = ['order__id', 'product__name']