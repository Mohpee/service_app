from django.contrib import admin
from django.db.models import Sum
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'payment_method', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order__id', 'transaction_id', 'order__client__username']
    readonly_fields = ['created_at', 'updated_at', 'transaction_id']
    raw_id_fields = ['order']
    list_editable = ['status']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order__client', 'order__service')

    def get_ordering(self, request):
        return ['-created_at']
