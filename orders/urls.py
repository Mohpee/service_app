from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/update-status/', views.OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('client/', views.ClientOrdersView.as_view(), name='client-orders'),
    path('provider/', views.ProviderOrdersView.as_view(), name='provider-orders'),
    path('book/<int:service_id>/', views.OrderBookingView.as_view(), name='order-booking'),
    path('book/<int:service_id>/success/', views.OrderBookingSuccessView.as_view(), name='order-booking-success'),
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversations'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_id>/messages/', views.MessageListCreateView.as_view(), name='conversation-messages'),
    path('service-requests/', views.ServiceRequestListCreateView.as_view(), name='service-requests'),
    path('service-requests/<int:pk>/', views.ServiceRequestDetailView.as_view(), name='service-request-detail'),
    # Notification endpoints
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/unread-count/', views.UnreadNotificationCountView.as_view(), name='unread-count'),
    path('notifications/mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='mark-all-read'),
    path('notifications/clear-all/', views.ClearAllNotificationsView.as_view(), name='clear-all-notifications'),
    path('notifications/settings/', views.NotificationSettingsView.as_view(), name='notification-settings'),
]