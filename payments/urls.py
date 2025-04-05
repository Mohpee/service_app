from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create/<int:order_id>/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('mpesa-callback/', views.MpesaCallbackView.as_view(), name='mpesa-callback'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment-history'),
]