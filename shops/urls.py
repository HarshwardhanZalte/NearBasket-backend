from django.urls import path
from . import views

urlpatterns = [
    path('my-shop/', views.get_my_shop, name='get_my_shop'),
    path('my-shop/update/', views.update_my_shop, name='update_my_shop'),
    path('details/<str:shop_id>/', views.shop_detail, name='shop_detail'),
    path('join/<str:shop_id>/', views.join_shop, name='join_shop'),
    path('add-customer/', views.add_customer, name='add_customer'),
    path('customers/', views.shop_customers, name='shop_customers'),
    path('customers/<int:user_id>/remove/', views.remove_customer, name='remove_customer'),
    path('my-joined-shops/', views.my_shops, name='my_shops'),
]