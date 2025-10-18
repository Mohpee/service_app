from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create/<int:order_id>/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('mpesa-callback/', views.MpesaCallbackView.as_view(), name='mpesa-callback'),
    path('stripe-webhook/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment-history'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('<int:payment_id>/refund/', views.PaymentRefundView.as_view(), name='payment-refund'),
]