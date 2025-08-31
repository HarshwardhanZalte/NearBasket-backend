from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import User, OTP

class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users in admin"""
    mobile_number = forms.CharField(max_length=10, help_text="10-digit mobile number")
    name = forms.CharField(max_length=100)
    
    class Meta:
        model = User
        fields = ('mobile_number', 'name', 'email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password fields optional for admin
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # For OTP-only users
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    """Form for updating users in admin"""
    class Meta:
        model = User
        fields = '__all__'

class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('mobile_number', 'name', 'email', 'role', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('mobile_number', 'name', 'email')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('mobile_number', 'password')}),
        ('Personal info', {'fields': ('name', 'email', 'address', 'profile_image_url', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile_number', 'name', 'email', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at',)

admin.site.register(User, UserAdmin)

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp_code', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__mobile_number', 'user__name']
    readonly_fields = ['created_at']