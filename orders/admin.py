from django.contrib import admin
from django.db.models import Count, Sum
from .models import Order, Notification, Conversation, Message, ServiceRequest

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'service', 'provider', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at', 'scheduled_date']
    search_fields = ['client__username', 'provider__username', 'service__name']
    readonly_fields = ['created_at', 'updated_at', 'total_amount']
    raw_id_fields = ['client', 'service', 'provider']
    list_editable = ['status']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'service', 'provider')

    def get_ordering(self, request):
        return ['-created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'is_sent', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_sent', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']
    readonly_fields = ['created_at']
    raw_id_fields = ['recipient', 'sender', 'related_order', 'related_service']
    list_editable = ['is_read']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'sender')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['subject', 'participants_count', 'last_message_time', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['subject', 'participants__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['participants']

    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Participants'

    def last_message_time(self, obj):
        last_msg = obj.messages.last()
        return last_msg.created_at if last_msg else None
    last_message_time.short_description = 'Last Message'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at', 'message_type']
    search_fields = ['sender__username', 'content']
    readonly_fields = ['created_at']
    raw_id_fields = ['conversation', 'sender']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'category', 'status', 'urgency', 'budget_range', 'assigned_provider', 'created_at']
    list_filter = ['status', 'urgency', 'category', 'created_at']
    search_fields = ['title', 'description', 'client__username']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['client', 'assigned_provider']
    list_editable = ['status', 'assigned_provider']

    fieldsets = (
        ('Request Details', {
            'fields': ('client', 'category', 'title', 'description')
        }),
        ('Requirements', {
            'fields': ('budget_min', 'budget_max', 'location', 'preferred_date', 'urgency', 'status')
        }),
        ('Assignment', {
            'fields': ('assigned_provider',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def budget_range(self, obj):
        return obj.get_budget_range()
    budget_range.short_description = 'Budget'
