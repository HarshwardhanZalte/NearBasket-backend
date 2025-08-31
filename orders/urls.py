from django.urls import path
from . import views

urlpatterns = [
    path('shops/<int:shop_id>/orders/', views.create_order, name='create_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('shops/<int:shop_id>/orders/list/', views.shop_orders, name='shop_orders'),
    path('<int:pk>/status/', views.update_order_status, name='update_order_status'),
]