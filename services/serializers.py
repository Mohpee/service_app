from rest_framework import serializers
from .models import Service, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'price',
            'category', 'category_id', 'image',
            'is_available', 'created_at', 'updated_at'
        ]