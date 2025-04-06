from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ACCOUNT_TYPES = (
        ('client', 'Client'),
        ('provider', 'Service Provider'),
        ('business', 'Business'),
    )
    
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='client')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Professional Information
    title = models.CharField(max_length=100, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Additional Details
    education = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    availability = models.CharField(max_length=50, blank=True)
    preferred_location = models.CharField(max_length=100, blank=True)
    
    # Social Links
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    # Profile completion tracking
    is_profile_complete = models.BooleanField(default=False)
    profile_completion_percentage = models.IntegerField(default=0)
    profile_completed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def calculate_profile_completion(self):
        required_fields = ['first_name', 'last_name', 'email', 'phone_number', 'bio']
        completed = sum(bool(getattr(self, field)) for field in required_fields)
        return (completed / len(required_fields)) * 100

    def save(self, *args, **kwargs):
        if not self._state.adding:  # Only calculate for existing users
            self.profile_completed = self.calculate_profile_completion() == 100
        super().save(*args, **kwargs)
