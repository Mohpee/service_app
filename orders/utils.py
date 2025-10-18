from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

def create_notification(recipient, notification_type, title, message, sender=None,
                       related_order=None, related_service=None, data=None):
    """
    Create a notification for a user
    """
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        title=title,
        message=message,
        related_order=related_order,
        related_service=related_service,
        data=data
    )
    return notification

def notify_order_status_change(order, old_status, new_status):
    """
    Send notifications when order status changes
    """
    if new_status == old_status:
        return

    if new_status == 'confirmed':
        # Notify client that order was confirmed
        create_notification(
            recipient=order.client,
            sender=order.provider,
            notification_type='order_confirmed',
            title='Order Confirmed',
            message=f'Your order for {order.service.name} has been confirmed by {order.provider.get_full_name()}',
            related_order=order,
            related_service=order.service
        )

    elif new_status == 'in_progress':
        # Notify client that service is in progress
        create_notification(
            recipient=order.client,
            sender=order.provider,
            notification_type='order_in_progress',
            title='Service Started',
            message=f'{order.provider.get_full_name()} has started working on your order for {order.service.name}',
            related_order=order,
            related_service=order.service
        )

    elif new_status == 'completed':
        # Notify client that order is completed
        create_notification(
            recipient=order.client,
            sender=order.provider,
            notification_type='order_completed',
            title='Order Completed',
            message=f'Your order for {order.service.name} has been completed by {order.provider.get_full_name()}',
            related_order=order,
            related_service=order.service
        )

        # Notify provider that order is completed
        create_notification(
            recipient=order.provider,
            sender=order.client,
            notification_type='order_completed',
            title='Order Completed',
            message=f'Order #{order.id} has been marked as completed',
            related_order=order,
            related_service=order.service
        )

    elif new_status == 'cancelled':
        # Notify relevant party about cancellation
        if old_status in ['pending', 'confirmed']:
            # Provider cancelled - notify client
            create_notification(
                recipient=order.client,
                sender=order.provider,
                notification_type='order_cancelled',
                title='Order Cancelled',
                message=f'Your order for {order.service.name} has been cancelled by {order.provider.get_full_name()}',
                related_order=order,
                related_service=order.service
            )
        else:
            # Client cancelled - notify provider
            create_notification(
                recipient=order.provider,
                sender=order.client,
                notification_type='order_cancelled',
                title='Order Cancelled',
                message=f'Order #{order.id} has been cancelled by the client',
                related_order=order,
                related_service=order.service
            )

def notify_payment_status_change(payment, old_status, new_status):
    """
    Send notifications when payment status changes
    """
    if new_status == old_status:
        return

    if new_status == 'completed':
        # Notify provider about payment
        create_notification(
            recipient=payment.order.provider,
            sender=payment.order.client,
            notification_type='payment_received',
            title='Payment Received',
            message=f'Payment of {payment.amount} received for order #{payment.order.id}',
            related_order=payment.order,
            related_service=payment.order.service
        )

    elif new_status == 'failed':
        # Notify client about payment failure
        create_notification(
            recipient=payment.order.client,
            sender=payment.order.provider,
            notification_type='payment_failed',
            title='Payment Failed',
            message=f'Payment for order #{payment.order.id} has failed. Please try again.',
            related_order=payment.order,
            related_service=payment.order.service
        )

def notify_new_review(review):
    """
    Send notification when a new review is posted
    """
    create_notification(
        recipient=review.provider,
        sender=review.client,
        notification_type='new_review',
        title='New Review Received',
        message=f'You received a {review.rating}-star review for {review.service.name}',
        related_order=review.service.orders.filter(client=review.client).first(),
        related_service=review.service
    )

def send_reminder_notifications():
    """
    Send reminder notifications for upcoming services
    This function can be called by a scheduled task
    """
    from django.utils import timezone
    from datetime import timedelta

    # Get orders scheduled for tomorrow
    tomorrow = timezone.now() + timedelta(days=1)
    upcoming_orders = Order.objects.filter(
        scheduled_date__date=tomorrow.date(),
        status__in=['confirmed', 'pending']
    )

    for order in upcoming_orders:
        # Notify client about upcoming service
        create_notification(
            recipient=order.client,
            notification_type='reminder',
            title='Upcoming Service Reminder',
            message=f'Reminder: You have a service scheduled for tomorrow - {order.service.name}',
            related_order=order,
            related_service=order.service
        )

        # Notify provider about upcoming service
        create_notification(
            recipient=order.provider,
            notification_type='reminder',
            title='Upcoming Service Reminder',
            message=f'Reminder: You have a service scheduled for tomorrow - {order.service.name}',
            related_order=order,
            related_service=order.service
        )