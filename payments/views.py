from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order
import stripe
from django.conf import settings
from .services import MpesaService
from rest_framework.views import APIView

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, client=request.user)
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response(
                {'error': 'Phone number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            mpesa = MpesaService()
            response = mpesa.stk_push(
                phone_number=phone_number,
                amount=order.total_amount,
                order_ref=order.id
            )
            
            if response.get('ResponseCode') == '0':
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    phone_number=phone_number,
                    merchant_request_id=response.get('MerchantRequestID'),
                    checkout_request_id=response.get('CheckoutRequestID')
                )
                
                return Response({
                    'status': 'success',
                    'message': 'Please complete the payment on your phone',
                    'payment_id': payment.id
                })
            
            return Response(
                {'error': response.get('ResponseDescription')},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class MpesaCallbackView(APIView):
    permission_classes = []  # Allow public access for M-Pesa callbacks

    def post(self, request):
        callback_data = request.data.get('Body', {}).get('stkCallback', {})
        
        payment = Payment.objects.filter(
            checkout_request_id=callback_data.get('CheckoutRequestID')
        ).first()
        
        if payment:
            if callback_data.get('ResultCode') == 0:
                payment.status = 'completed'
                # Get transaction details from callback data
                payment.transaction_id = callback_data.get('CallbackMetadata', {}).get('Item', [])[1].get('Value')
                payment.save()
                
                # Update order status
                payment.order.status = 'confirmed'
                payment.order.save()
            else:
                payment.status = 'failed'
                payment.save()
        
        return Response(status=status.HTTP_200_OK)

class PaymentVerificationView(generics.UpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'transaction_id'

    def patch(self, request, *args, **kwargs):
        payment = self.get_object()
        payment.mark_as_completed()
        return Response({'status': 'payment completed'})

class PaymentHistoryView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            order__client=self.request.user
        ).select_related('order')
