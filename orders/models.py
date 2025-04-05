from django.db import models
from django.conf import settings
from services.models import Service

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.id} by {self.client.username}"

    def save(self, *args, **kwargs):
        self.total_amount = self.service.price * self.quantity
        super().save(*args, **kwargs)

    def get_total_amount(self):
        return self.service.price * self.quantity

    def update_status(self, new_status):
        if new_status in dict(self.STATUS_CHOICES):
            self.status = new_status
            self.save()
            return True
        return False
