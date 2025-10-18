from rest_framework import serializers
from .models import Service, Category, ServicePackage, FavoriteService, ProviderSchedule, Promotion

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    provider_name = serializers.CharField(source='provider.get_full_name', read_only=True)
    provider_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id', 'provider', 'name', 'description', 'price', 'base_price',
            'category', 'category_id', 'image', 'additional_images',
            'location', 'latitude', 'longitude',
            'is_available', 'availability_type', 'working_hours',
            'has_packages', 'packages',
            'experience_years', 'qualifications', 'languages',
            'total_bookings', 'rating',
            'provider_name', 'provider_rating', 'reviews_count', 'is_bookmarked',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_bookings', 'rating', 'created_at', 'updated_at']

    def get_provider_rating(self, obj):
        return obj.average_rating

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in [review.client for review in obj.reviews.all()]
        return False

class ServicePackageSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = ServicePackage
        fields = [
            'id', 'service', 'service_name', 'name', 'description', 'price',
            'duration_hours', 'features', 'is_popular', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class FavoriteServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_price = serializers.DecimalField(source='service.price', max_digits=10, decimal_places=2, read_only=True)
    provider_name = serializers.CharField(source='service.provider.get_full_name', read_only=True)

    class Meta:
        model = FavoriteService
        fields = [
            'id', 'user', 'service', 'service_name', 'service_price', 'provider_name', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

class ProviderScheduleSerializer(serializers.ModelSerializer):
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = ProviderSchedule
        fields = [
            'id', 'provider', 'day_of_week', 'day_name', 'start_time', 'end_time',
            'is_available', 'date_override', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_day_name(self, obj):
        return dict(obj._meta.get_field('day_of_week').choices)[obj.day_of_week]

class PromotionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    provider_name = serializers.CharField(source='provider.get_full_name', read_only=True)
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = [
            'id', 'title', 'description', 'discount_type', 'discount_value',
            'applicable_to', 'category', 'category_name', 'service', 'service_name',
            'provider', 'provider_name', 'start_date', 'end_date', 'usage_limit',
            'usage_count', 'is_active', 'promo_code', 'is_valid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at']

    def get_is_valid(self, obj):
        return obj.is_valid()