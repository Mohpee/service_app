from django.db import models
from django.conf import settings
from django.utils import timezone
from services.models import Service

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='orders')
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provided_orders')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Scheduling information
    scheduled_date = models.DateTimeField(null=True, blank=True)
    duration_hours = models.PositiveIntegerField(default=1, help_text="Duration in hours")
    is_flexible_timing = models.BooleanField(default=False)

    # Location and delivery
    delivery_address = models.TextField(blank=True, null=True)
    service_location = models.CharField(max_length=255, blank=True, help_text="Where service will be provided")

    # Communication
    notes = models.TextField(blank=True, null=True)
    special_requirements = models.TextField(blank=True, null=True)

    # Provider response
    provider_notes = models.TextField(blank=True, null=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.id} by {self.client.username}"

    def save(self, *args, **kwargs):
        # Set provider from service if not already set
        if not self.provider_id:
            self.provider = self.service.provider

        # Calculate total amount
        self.total_amount = self.service.price * self.quantity

        # Update status timestamps
        if self.status == 'confirmed' and not self.confirmed_at:
            self.confirmed_at = timezone.now()
        elif self.status == 'in_progress' and not self.started_at:
            self.started_at = timezone.now()
        elif self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)

    def get_total_amount(self):
        return self.service.price * self.quantity

    def update_status(self, new_status):
        if new_status in dict(self.STATUS_CHOICES):
            self.status = new_status
            self.save()
            return True
        return False

    def can_be_cancelled(self):
        """Check if order can still be cancelled"""
        return self.status in ['pending', 'confirmed']

    def is_overdue(self):
        """Check if service is overdue"""
        if self.status in ['completed', 'cancelled']:
            return False
        if self.scheduled_date and timezone.now() > self.scheduled_date:
            return True
        return False

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('order_confirmed', 'Order Confirmed'),
        ('order_cancelled', 'Order Cancelled'),
        ('order_completed', 'Order Completed'),
        ('payment_received', 'Payment Received'),
        ('new_message', 'New Message'),
        ('reminder', 'Reminder'),
        ('promotion', 'Promotion'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)
    related_service = models.ForeignKey('services.Service', on_delete=models.CASCADE, null=True, blank=True)

    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)  # For push notifications
    data = models.JSONField(null=True, blank=True, help_text="Additional data for the notification")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def mark_as_sent(self):
        self.is_sent = True
        self.save()

class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    related_order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)
    related_service = models.ForeignKey('services.Service', on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation: {self.subject}"

    def get_other_participant(self, user):
        """Get the other participant in the conversation"""
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=[
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File')
    ], default='text')
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username}: {self.content[:50]}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update conversation timestamp
        self.conversation.updated_at = self.created_at
        self.conversation.save()

class ServiceRequest(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests')
    category = models.ForeignKey('services.Category', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=255)
    preferred_date = models.DateTimeField(null=True, blank=True)
    urgency = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium')
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('quoted', 'Quoted'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='open')
    assigned_provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service Request'
        verbose_name_plural = 'Service Requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Request: {self.title}"

    def get_budget_range(self):
        if self.budget_min and self.budget_max:
            return f"KES {self.budget_min} - KES {self.budget_max}"
        elif self.budget_min:
            return f"KES {self.budget_min}+"
        elif self.budget_max:
            return f"Up to KES {self.budget_max}"
        return "Budget not specified"
