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
        payment_method = request.data.get('payment_method', 'mpesa')

        # Check if payment already exists
        if hasattr(order, 'payment') and order.payment.status != 'failed':
            return Response(
                {'error': 'Payment already exists for this order'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if payment_method == 'mpesa':
            return self._create_mpesa_payment(request, order)
        elif payment_method == 'card':
            return self._create_card_payment(request, order)
        else:
            return Response(
                {'error': 'Invalid payment method'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _create_mpesa_payment(self, request, order):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response(
                {'error': 'Phone number is required for M-Pesa payments'},
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
                    payment_method='mpesa',
                    phone_number=phone_number,
                    merchant_request_id=response.get('MerchantRequestID'),
                    checkout_request_id=response.get('CheckoutRequestID')
                )

                return Response({
                    'status': 'success',
                    'message': 'Please complete the payment on your phone',
                    'payment_id': payment.id,
                    'payment_method': 'mpesa'
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

    def _create_card_payment(self, request, order):
        # For card payments, we'll create a payment record and redirect to Stripe
        try:
            # Create Stripe Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency='usd',
                metadata={'order_id': order.id}
            )

            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                payment_method='card',
                stripe_payment_intent_id=intent.id,
                status='processing'
            )

            return Response({
                'status': 'success',
                'message': 'Redirect to complete card payment',
                'payment_id': payment.id,
                'payment_method': 'card',
                'stripe_client_secret': intent.client_secret,
                'stripe_publishable_key': settings.STRIPE_PUBLIC_KEY
            })

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
        user = self.request.user
        if user.account_type == 'client':
            return Payment.objects.filter(order__client=user).select_related('order')
        elif user.account_type in ['provider', 'business']:
            return Payment.objects.filter(order__provider=user).select_related('order')
        return Payment.objects.none()

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'client':
            return Payment.objects.filter(order__client=user)
        elif user.account_type in ['provider', 'business']:
            return Payment.objects.filter(order__provider=user)
        return Payment.objects.none()

class StripeWebhookView(APIView):
    """Handle Stripe webhooks"""
    permission_classes = []  # Public access for webhooks

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self._handle_successful_payment(payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self._handle_failed_payment(payment_intent)

        return Response(status=status.HTTP_200_OK)

    def _handle_successful_payment(self, payment_intent):
        payment = Payment.objects.filter(
            stripe_payment_intent_id=payment_intent['id']
        ).first()

        if payment:
            payment.status = 'completed'
            payment.transaction_id = payment_intent['id']
            payment.metadata = payment_intent
            payment.save()

            # Update order status
            payment.order.status = 'confirmed'
            payment.order.save()

            # Create notification
            from orders.models import Notification
            Notification.objects.create(
                recipient=payment.order.provider,
                sender=payment.order.client,
                notification_type='payment_received',
                title='Payment Received',
                message=f'Payment of {payment.amount} received for order #{payment.order.id}',
                related_order=payment.order,
                related_service=payment.order.service
            )

    def _handle_failed_payment(self, payment_intent):
        payment = Payment.objects.filter(
            stripe_payment_intent_id=payment_intent['id']
        ).first()

        if payment:
            payment.status = 'failed'
            payment.error_message = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
            payment.save()

class PaymentRefundView(generics.CreateAPIView):
    """Process payment refunds"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, order__provider=request.user)

        if payment.status != 'completed':
            return Response(
                {'error': 'Only completed payments can be refunded'},
                status=status.HTTP_400_BAD_REQUEST
            )

        refund_amount = request.data.get('amount')
        if not refund_amount:
            refund_amount = payment.amount

        try:
            if payment.payment_method == 'card' and payment.stripe_payment_intent_id:
                # Process Stripe refund
                refund = stripe.Refund.create(
                    payment_intent=payment.stripe_payment_intent_id,
                    amount=int(float(refund_amount) * 100)
                )

                payment.refund_amount = refund_amount
                payment.refund_transaction_id = refund.id
                payment.status = 'refunded' if refund_amount >= payment.amount else 'partially_refunded'
                payment.save()

            elif payment.payment_method == 'mpesa':
                # For M-Pesa, you'd implement B2C refund logic here
                # This is a simplified version
                payment.refund_amount = refund_amount
                payment.status = 'refunded' if refund_amount >= payment.amount else 'partially_refunded'
                payment.save()

            # Update order status if fully refunded
            if refund_amount >= payment.amount:
                payment.order.status = 'refunded'
                payment.order.save()

            return Response({
                'status': 'success',
                'message': 'Refund processed successfully',
                'refund_amount': refund_amount
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PaymentHistoryView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'client':
            return Payment.objects.filter(order__client=user).select_related('order')
        elif user.account_type in ['provider', 'business']:
            return Payment.objects.filter(order__provider=user).select_related('order')
        return Payment.objects.none()
