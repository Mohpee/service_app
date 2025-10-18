from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Order, Notification, Conversation, Message, ServiceRequest
from .serializers import OrderSerializer, ConversationSerializer, MessageSerializer, ServiceRequestSerializer
from .serializers import OrderSerializer, NotificationSerializer
from users.permissions import IsClient, IsProvider, CanManageOrder

class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'client':
            return Order.objects.filter(client=user)
        elif user.account_type in ['provider', 'business']:
            return Order.objects.filter(provider=user)
        return Order.objects.none()

    def perform_create(self, serializer):
        service = serializer.validated_data['service']
        serializer.save(client=self.request.user, provider=service.provider)

        # Create notification for provider
        Notification.objects.create(
            recipient=service.provider,
            sender=self.request.user,
            notification_type='new_order',
            title='New Order Received',
            message=f'You have received a new order for {service.name}',
            related_order=serializer.instance,
            related_service=service
        )

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [CanManageOrder()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'client':
            return Order.objects.filter(client=user)
        elif user.account_type in ['provider', 'business']:
            return Order.objects.filter(provider=user)
        return Order.objects.none()

class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        return [CanManageOrder()]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        old_status = self.get_object().status
        new_status = serializer.validated_data.get('status', old_status)

        serializer.save()

        # Create notifications based on status change
        order = self.get_object()

        if new_status != old_status:
            if new_status == 'confirmed':
                # Notify client
                Notification.objects.create(
                    recipient=order.client,
                    sender=order.provider,
                    notification_type='order_confirmed',
                    title='Order Confirmed',
                    message=f'Your order for {order.service.name} has been confirmed',
                    related_order=order,
                    related_service=order.service
                )
            elif new_status == 'completed':
                # Notify client
                Notification.objects.create(
                    recipient=order.client,
                    sender=order.provider,
                    notification_type='order_completed',
                    title='Order Completed',
                    message=f'Your order for {order.service.name} has been completed',
                    related_order=order,
                    related_service=order.service
                )

class ClientOrdersView(generics.ListAPIView):
    """List orders for clients"""
    serializer_class = OrderSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user)

class ProviderOrdersView(generics.ListAPIView):
    """List orders for providers"""
    serializer_class = OrderSerializer
    permission_classes = [IsProvider]

    def get_queryset(self):
        return Order.objects.filter(provider=self.request.user)

class OrderBookingView(APIView):
    """Create a booking for a service"""
    permission_classes = [IsClient]

    def post(self, request, service_id):
        from services.models import Service

        try:
            service = Service.objects.get(id=service_id, is_available=True)
        except Service.DoesNotExist:
            return Response(
                {'error': 'Service not found or not available'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if user already has a pending order for this service
        existing_order = Order.objects.filter(
            client=request.user,
            service=service,
            status__in=['pending', 'confirmed']
        ).first()

        if existing_order:
            return Response(
                {'error': 'You already have a pending order for this service'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the order
        order = Order.objects.create(
            client=request.user,
            service=service,
            provider=service.provider,
            quantity=request.data.get('quantity', 1),
            scheduled_date=request.data.get('scheduled_date'),
            delivery_address=request.data.get('delivery_address'),
            notes=request.data.get('notes'),
            special_requirements=request.data.get('special_requirements')
        )

        # Create notification for provider
        Notification.objects.create(
            recipient=service.provider,
            sender=request.user,
            notification_type='new_order',
            title='New Order Received',
            message=f'You have received a new order for {service.name}',
            related_order=order,
            related_service=service
        )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ConversationListCreateView(generics.ListCreateAPIView):
    """List and create conversations"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        participants = serializer.validated_data['participants']
        participants.append(self.request.user)
        serializer.save(participants=participants)

class ConversationDetailView(generics.RetrieveAPIView):
    """Get conversation details"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

class MessageListCreateView(generics.ListCreateAPIView):
    """List and create messages in a conversation"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(conversation_id=conversation_id)

    def perform_create(self, serializer):
        conversation_id = self.kwargs['conversation_id']
        conversation = Conversation.objects.get(id=conversation_id, participants=self.request.user)
        serializer.save(conversation=conversation, sender=self.request.user)

class ServiceRequestListCreateView(generics.ListCreateAPIView):
    """List and create service requests"""
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'client':
            return ServiceRequest.objects.filter(client=user)
        elif user.account_type in ['provider', 'business']:
            return ServiceRequest.objects.filter(assigned_provider=user)
        return ServiceRequest.objects.none()

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

class ServiceRequestDetailView(generics.RetrieveUpdateAPIView):
    """Get and update service requests"""
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'client':
            return ServiceRequest.objects.filter(client=user)
        elif user.account_type in ['provider', 'business']:
            return ServiceRequest.objects.filter(assigned_provider=user)
        return ServiceRequest.objects.none()

class NotificationListView(generics.ListAPIView):
    """List notifications for the current user"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """Get and update notification status"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def patch(self, request, *args, **kwargs):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'notification marked as read'})

class UnreadNotificationCountView(APIView):
    """Get count of unread notifications"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        return Response({'unread_count': count})

class MarkAllNotificationsReadView(APIView):
    """Mark all notifications as read"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )

        count = notifications.count()
        notifications.update(is_read=True)

        return Response({
            'status': 'success',
            'marked_count': count
        })

class NotificationSettingsView(APIView):
    """Get and update notification settings"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # For now, return default settings
        # In a real app, you'd store these in the user model or a separate settings model
        settings = {
            'order_notifications': True,
            'payment_notifications': True,
            'review_notifications': True,
            'promotion_notifications': False,
            'email_notifications': True,
            'push_notifications': True
        }
        return Response(settings)

    def post(self, request):
        # Update notification settings
        # In a real app, you'd save these to the database
        return Response({
            'status': 'settings updated',
            'settings': request.data
        })
