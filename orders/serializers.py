from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'client', 'service', 'status', 'quantity',
            'total_amount', 'delivery_address', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['client', 'total_amount', 'created_at', 'updated_at']