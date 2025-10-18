from django.contrib import admin
from django.db.models import Count, Sum, Avg
from .models import Service, Category, Review, ServicePackage, FavoriteService, ProviderSchedule, Promotion

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'services_count', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    readonly_fields = ['services_count']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(services_count=Count('services'))

    def services_count(self, obj):
        return obj.services_count
    services_count.short_description = 'Services Count'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'category', 'price', 'rating', 'total_bookings', 'is_available', 'created_at']
    list_filter = ['is_available', 'category', 'created_at', 'rating']
    search_fields = ['name', 'description', 'provider__username', 'provider__email']
    readonly_fields = ['total_bookings', 'rating', 'created_at', 'updated_at']
    raw_id_fields = ['provider']
    list_editable = ['is_available', 'price']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('provider', 'category')

    def get_ordering(self, request):
        return ['-created_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['service', 'client', 'provider', 'rating', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['service__name', 'client__username', 'provider__username']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['service', 'client', 'provider']

@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'service', 'price', 'duration_hours', 'is_popular', 'is_active']
    list_filter = ['is_popular', 'is_active', 'created_at']
    search_fields = ['name', 'service__name']
    raw_id_fields = ['service']
    list_editable = ['is_popular', 'is_active']

@admin.register(FavoriteService)
class FavoriteServiceAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'service__name']
    raw_id_fields = ['user', 'service']

@admin.register(ProviderSchedule)
class ProviderScheduleAdmin(admin.ModelAdmin):
    list_display = ['provider', 'day_of_week', 'start_time', 'end_time', 'is_available', 'date_override']
    list_filter = ['day_of_week', 'is_available', 'date_override']
    search_fields = ['provider__username']
    raw_id_fields = ['provider']
    list_editable = ['is_available']

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'discount_type', 'discount_value', 'is_active', 'is_valid', 'usage_count', 'start_date', 'end_date']
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['title', 'description', 'promo_code']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    list_editable = ['is_active']

    fieldsets = (
        ('Promotion Details', {
            'fields': ('title', 'description', 'promo_code')
        }),
        ('Discount Settings', {
            'fields': ('discount_type', 'discount_value', 'applicable_to', 'category', 'service', 'provider')
        }),
        ('Validity Period', {
            'fields': ('start_date', 'end_date', 'usage_limit')
        }),
        ('Status', {
            'fields': ('is_active', 'usage_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Currently Valid'
