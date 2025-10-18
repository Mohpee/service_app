from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from .models import Order, Notification
from services.models import Service, Category

User = get_user_model()

class OrderModelTest(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user(
            username='provider',
            email='provider@test.com',
            password='testpass123',
            account_type='provider'
        )
        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123',
            account_type='client'
        )
        self.category = Category.objects.create(
            name='HOME',
            description='Home services'
        )
        self.service = Service.objects.create(
            provider=self.provider,
            category=self.category,
            name='Test Service',
            description='Test service',
            price=50.00,
            location='Nairobi'
        )

    def test_order_creation(self):
        order = Order.objects.create(
            client=self.client_user,
            service=self.service,
            provider=self.provider,
            quantity=2,
            delivery_address='Test Address'
        )
        self.assertEqual(order.client, self.client_user)
        self.assertEqual(order.service, self.service)
        self.assertEqual(order.provider, self.provider)
        self.assertEqual(order.total_amount, 100.00)  # 50 * 2
        self.assertEqual(order.status, 'pending')

    def test_order_total_calculation(self):
        order = Order.objects.create(
            client=self.client_user,
            service=self.service,
            provider=self.provider,
            quantity=3
        )
        self.assertEqual(order.total_amount, 150.00)

class NotificationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )

    def test_notification_creation(self):
        notification = Notification.objects.create(
            recipient=self.user1,
            sender=self.user2,
            notification_type='order_confirmed',
            title='Order Confirmed',
            message='Your order has been confirmed'
        )
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.sender, self.user2)
        self.assertEqual(notification.notification_type, 'order_confirmed')
        self.assertFalse(notification.is_read)

class OrderAPITest(APITestCase):
    def setUp(self):
        self.provider = User.objects.create_user(
            username='provider',
            email='provider@test.com',
            password='testpass123',
            account_type='provider'
        )
        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123',
            account_type='client'
        )
        self.category = Category.objects.create(
            name='HOME',
            description='Home services'
        )
        self.service = Service.objects.create(
            provider=self.provider,
            category=self.category,
            name='Test Service',
            description='Test service',
            price=50.00,
            location='Nairobi'
        )

    def test_order_creation(self):
        self.client.force_authenticate(user=self.client_user)
        url = reverse('orders:order-list-create')
        data = {
            'service': self.service.id,
            'quantity': 1,
            'delivery_address': 'Test Address'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that order was created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.client, self.client_user)
        self.assertEqual(order.service, self.service)

    def test_order_list_client(self):
        # Create an order
        Order.objects.create(
            client=self.client_user,
            service=self.service,
            provider=self.provider
        )

        self.client.force_authenticate(user=self.client_user)
        url = reverse('orders:order-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_order_list_provider(self):
        # Create an order
        Order.objects.create(
            client=self.client_user,
            service=self.service,
            provider=self.provider
        )

        self.client.force_authenticate(user=self.provider)
        url = reverse('orders:order-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
