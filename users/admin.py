from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Sum
from .models import User, BusinessProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'account_type', 'first_name', 'last_name', 'is_active', 'date_joined']
    list_filter = ['account_type', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('account_type', 'phone_number', 'bio', 'profile_picture')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('account_type', 'phone_number', 'bio')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            services_count=Count('services'),
            orders_count=Count('orders')
        )

@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'business_type', 'verification_status', 'created_at']
    list_filter = ['verification_status', 'business_type', 'created_at']
    search_fields = ['business_name', 'user__username', 'user__email', 'registration_number']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Business Information', {
            'fields': ('user', 'business_name', 'business_type', 'description', 'logo')
        }),
        ('Legal Information', {
            'fields': ('registration_number', 'tax_id')
        }),
        ('Contact Information', {
            'fields': ('business_address', 'business_phone', 'website')
        }),
        ('Verification', {
            'fields': ('verification_status', 'verification_documents', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['verify_businesses', 'reject_businesses']

    def verify_businesses(self, request, queryset):
        queryset.update(verification_status='verified')
        self.message_user(request, f"{queryset.count()} business(es) verified successfully.")
    verify_businesses.short_description = "Verify selected businesses"

    def reject_businesses(self, request, queryset):
        queryset.update(verification_status='rejected')
        self.message_user(request, f"{queryset.count()} business(es) rejected.")
    reject_businesses.short_description = "Reject selected businesses"
