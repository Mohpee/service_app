from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'is_active', 'profile_completion_status', 'show_profile_picture')
    list_filter = ('is_active', 'date_joined', 'profile_completed')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'email', 
                'phone_number', 'profile_picture', 'bio'
            )
        }),
        ('Skills & Location', {
            'fields': ('skills', 'preferred_location')
        }),
        ('Status', {
            'fields': ('is_active', 'profile_completed')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def profile_completion_status(self, obj):
        percentage = obj.calculate_profile_completion()
        if percentage == 100:
            return format_html('<span style="color: green;">Complete</span>')
        return format_html('<span style="color: orange;">{}%</span>', percentage)
    
    profile_completion_status.short_description = 'Profile Status'

    def show_profile_picture(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return "No picture"
    
    show_profile_picture.short_description = 'Profile Picture'
