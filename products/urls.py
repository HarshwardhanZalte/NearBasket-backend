from django.urls import path
from . import views

urlpatterns = [
    path('shops/<int:shop_id>/products/', views.product_list_create, name='product_list_create'),
    path('shops/<int:shop_id>/products/<int:pk>/', views.product_detail, name='product_detail'),
]