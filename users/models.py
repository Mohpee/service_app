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
