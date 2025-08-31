from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop_list_create, name='shop_list_create'),
    path('<int:pk>/', views.shop_detail, name='shop_detail'),
    path('<str:pk>/join/', views.join_shop, name='join_shop'),  # Uses shop_id
    path('<int:pk>/add-customer/', views.add_customer, name='add_customer'),
    path('<int:pk>/customers/', views.shop_customers, name='shop_customers'),
    path('<int:pk>/customers/<int:user_id>/', views.remove_customer, name='remove_customer'),
    path('my-shops/', views.my_shops, name='my_shops'),
]