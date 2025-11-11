from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('me/', views.get_profile, name='profile'),
    path('me/update/', views.update_profile, name='update_profile'),
    
    path('job/', views.tigger_job, name='tigger_job'),
]