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
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business_profile')
    business_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    business_address = models.TextField()
    business_phone = models.CharField(max_length=15)
    website = models.URLField(blank=True)
    description = models.TextField()
    logo = models.ImageField(upload_to='business_logos/', blank=True)

    verification_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ], default='pending')

    verification_documents = models.JSONField(null=True, blank=True, help_text="Store document URLs")
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Business Profile'
        verbose_name_plural = 'Business Profiles'

    def __str__(self):
        return f"{self.business_name} - {self.user.username}"

    def is_verified(self):
        return self.verification_status == 'verified'
