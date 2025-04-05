from django_daraja.mpesa.core import MpesaClient
from django.conf import settings
from datetime import datetime

class MpesaPayment:
    def __init__(self):
        self.cl = MpesaClient()
        self.callback_url = "https://your-domain/api/payments/mpesa-callback/"
    
    def stk_push(self, phone_number, amount, order_ref):
        phone = int(phone_number)
        amount = int(amount)
        account_reference = f'Order#{order_ref}'
        transaction_desc = f'Payment for Order#{order_ref}'
        
        response = self.cl.stk_push(
            phone_number=phone,
            amount=amount,
            account_reference=account_reference,
            transaction_desc=transaction_desc,
            callback_url=self.callback_url
        )
        
        return response