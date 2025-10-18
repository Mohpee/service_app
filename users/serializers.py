from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import BusinessProfile

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'email', 'first_name', 'last_name',
                 'account_type', 'phone_number', 'bio')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'account_type': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    services_count = serializers.SerializerMethodField()
    orders_count = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'account_type',
                 'phone_number', 'bio', 'profile_picture', 'created_at', 'updated_at',
                 'services_count', 'orders_count', 'reviews_count', 'average_rating')
        read_only_fields = ('id', 'created_at', 'updated_at', 'services_count', 'orders_count', 'reviews_count', 'average_rating')

    def get_services_count(self, obj):
        if obj.account_type in ['provider', 'business']:
            return obj.services.count()
        return 0

    def get_orders_count(self, obj):
        if obj.account_type == 'client':
            return obj.orders.count()
        elif obj.account_type in ['provider', 'business']:
            return obj.provided_orders.count()
        return 0

    def get_reviews_count(self, obj):
        if obj.account_type in ['provider', 'business']:
            return obj.received_reviews.count()
        return 0

    def get_average_rating(self, obj):
        if obj.account_type in ['provider', 'business']:
            reviews = obj.received_reviews.all()
            if reviews:
                return sum(review.rating for review in reviews) / len(reviews)
        return 0

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'bio', 'profile_picture')

class BusinessProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = BusinessProfile
        fields = [
            'id', 'user', 'user_name', 'user_email', 'business_name', 'business_type',
            'registration_number', 'tax_id', 'business_address', 'business_phone',
            'website', 'description', 'logo', 'verification_status', 'verification_documents',
            'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'verification_status', 'rejection_reason', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)