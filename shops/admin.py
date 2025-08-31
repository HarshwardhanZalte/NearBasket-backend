from django.contrib import admin
from .models import Shop, ShopCustomer

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'shop_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'owner__name', 'shop_id']
    readonly_fields = ['shop_id', 'created_at']

@admin.register(ShopCustomer)
class ShopCustomerAdmin(admin.ModelAdmin):
    list_display = ['shop', 'customer', 'joined_at']
    list_filter = ['joined_at']
    search_fields = ['shop__name', 'customer__name']