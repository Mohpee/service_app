from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('HOME', 'Home & Personal Services'),
        ('FOOD', 'Food & Catering Services'),
        ('BEAUTY', 'Beauty & Wellness'),
        ('CREATIVE', 'Creative & Talent Services'),
        ('RETAIL', 'Products & Retail Services'),
        ('PROF', 'Professional & Technical Services'),
        ('TRANSPORT', 'Transport & Delivery Services'),
        ('AGENCY', 'Agency & Business Services'),
        ('EDU', 'Education & Training Services'),
    ]
    
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.get_name_display()

class Service(models.Model):
    AVAILABILITY_CHOICES = [
        ('ALWAYS', '24/7'),
        ('WEEKDAY', 'Weekdays Only'),
        ('WEEKEND', 'Weekends Only'),
        ('CUSTOM', 'Custom Hours'),
    ]
    
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='services/')
    additional_images = models.JSONField(null=True, blank=True, help_text="Store multiple image URLs")
    
    # Location information
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Availability and scheduling
    is_available = models.BooleanField(default=True)
    availability_type = models.CharField(max_length=10, choices=AVAILABILITY_CHOICES, default='CUSTOM')
    working_hours = models.JSONField(null=True, blank=True, help_text="Store working hours for each day")
    
    # Pricing and packages
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    has_packages = models.BooleanField(default=False)
    packages = models.JSONField(null=True, blank=True, help_text="Store different service packages and their prices")
    
    # Service specific fields
    experience_years = models.PositiveIntegerField(default=0)
    qualifications = models.TextField(null=True, blank=True)
    languages = models.JSONField(null=True, blank=True, help_text="List of languages spoken")
    
    # Metrics
    total_bookings = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, 
                               validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('services:service-detail', kwargs={'pk': self.pk})

    @property
    def average_rating(self):
        ratings = self.reviews.all().values_list('rating', flat=True)
        if ratings:
            return sum(ratings) / len(ratings)
        return 0

class Review(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_reviews')
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False, help_text="Verified if client actually used the service")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['service', 'client']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.client.username} for {self.service.name}"

    def save(self, *args, **kwargs):
        # Set the provider from the service when saving
        if not self.provider_id:
            self.provider = self.service.provider
        super().save(*args, **kwargs)

class ServicePackage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_packages')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_hours = models.PositiveIntegerField()
    features = models.JSONField(help_text="List of features included")
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service Package'
        verbose_name_plural = 'Service Packages'
        ordering = ['price']

    def __str__(self):
        return f"{self.service.name} - {self.name}"

class FavoriteService(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'service']
        verbose_name = 'Favorite Service'
        verbose_name_plural = 'Favorite Services'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} favorited {self.service.name}"

class ProviderSchedule(models.Model):
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedule')
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    date_override = models.DateField(null=True, blank=True, help_text="For specific date overrides")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Provider Schedule'
        verbose_name_plural = 'Provider Schedules'
        unique_together = ['provider', 'day_of_week', 'date_override']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        day_name = dict(self._meta.get_field('day_of_week').choices)[self.day_of_week]
        return f"{self.provider.username} - {day_name}"

class Promotion(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    discount_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    applicable_to = models.CharField(max_length=20, choices=[
        ('all', 'All Services'),
        ('category', 'Specific Category'),
        ('service', 'Specific Service'),
        ('provider', 'Specific Provider')
    ])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    promo_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (self.is_active and
                self.start_date <= now <= self.end_date and
                (self.usage_limit is None or self.usage_count < self.usage_limit))

    def apply_discount(self, original_price):
        if not self.is_valid():
            return original_price

        if self.discount_type == 'percentage':
            discount = original_price * (self.discount_value / 100)
        else:  # fixed
            discount = min(self.discount_value, original_price)

        return max(0, original_price - discount)
