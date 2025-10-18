from rest_framework import serializers
from .models import Order, Notification, Conversation, Message, ServiceRequest

class OrderSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    provider_name = serializers.CharField(source='provider.get_full_name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    can_cancel = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'client', 'service', 'provider', 'status', 'quantity',
            'total_amount', 'scheduled_date', 'duration_hours', 'is_flexible_timing',
            'delivery_address', 'service_location', 'notes', 'special_requirements',
            'provider_notes', 'estimated_completion',
            'service_name', 'provider_name', 'client_name',
            'can_cancel', 'is_overdue',
            'created_at', 'updated_at', 'confirmed_at', 'started_at', 'completed_at'
        ]
        read_only_fields = ['client', 'provider', 'total_amount', 'created_at', 'updated_at',
                           'confirmed_at', 'started_at', 'completed_at']

    def get_can_cancel(self, obj):
        return obj.can_be_cancelled()

    def get_is_overdue(self, obj):
        return obj.is_overdue()

class ConversationSerializer(serializers.ModelSerializer):
    participants_names = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participants_names', 'related_order', 'related_service',
            'subject', 'last_message', 'unread_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_participants_names(self, obj):
        return [user.get_full_name() or user.username for user in obj.participants.all()]

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'content': last_msg.content[:100],
                'sender': last_msg.sender.get_full_name() or last_msg.sender.username,
                'created_at': last_msg.created_at
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_name', 'content', 'message_type',
            'attachment', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'sender', 'sender_name', 'created_at']

class ServiceRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    budget_range = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'client', 'client_name', 'category', 'category_name', 'title', 'description',
            'budget_min', 'budget_max', 'budget_range', 'location', 'preferred_date',
            'urgency', 'status', 'assigned_provider', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client', 'client_name', 'created_at', 'updated_at']

    def get_budget_range(self, obj):
        return obj.get_budget_range()

class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    related_order_id = serializers.IntegerField(source='related_order.id', read_only=True)
    related_service_name = serializers.CharField(source='related_service.name', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'is_read', 'is_sent',
            'sender', 'sender_name', 'related_order', 'related_order_id',
            'related_service', 'related_service_name', 'data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'sender']

class OrderNotificationSerializer(serializers.ModelSerializer):
    """Serializer for order-related notifications"""
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']