from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    order_details = serializers.SerializerMethodField()
    can_refund = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'payment_method', 'status',
            'phone_number', 'transaction_id', 'card_last4', 'card_brand',
            'error_message', 'refund_amount', 'metadata',
            'order_details', 'can_refund',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['transaction_id', 'status', 'created_at', 'updated_at', 'card_last4', 'card_brand']

    def get_order_details(self, obj):
        return {
            'id': obj.order.id,
            'service_name': obj.order.service.name,
            'provider_name': obj.order.provider.get_full_name(),
            'client_name': obj.order.client.get_full_name(),
        }

    def get_can_refund(self, obj):
        return obj.status == 'completed' and obj.refund_amount == 0