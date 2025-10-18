from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Service, Category, Review

User = get_user_model()

class ServiceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testprovider',
            email='provider@test.com',
            password='testpass123',
            account_type='provider'
        )
        self.client_user = User.objects.create_user(
            username='testclient',
            email='client@test.com',
            password='testpass123',
            account_type='client'
        )
        self.category = Category.objects.create(
            name='HOME',
            description='Home services'
        )

    def test_service_creation(self):
        service = Service.objects.create(
            provider=self.user,
            category=self.category,
            name='Test Cleaning Service',
            description='Professional cleaning service',
            price=50.00,
            location='Nairobi, Kenya'
        )
        self.assertEqual(service.name, 'Test Cleaning Service')
        self.assertEqual(service.provider, self.user)
        self.assertEqual(service.price, 50.00)
        self.assertTrue(service.is_available)

    def test_service_str_method(self):
        service = Service.objects.create(
            provider=self.user,
            category=self.category,
            name='Test Service',
            description='Test description',
            price=25.00,
            location='Test Location'
        )
        self.assertEqual(str(service), 'Test Service')

class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(
            name='BEAUTY',
            description='Beauty and wellness services'
        )
        self.assertEqual(category.name, 'BEAUTY')
        self.assertEqual(category.get_name_display(), 'Beauty & Wellness')

class ReviewModelTest(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user(
            username='provider',
            email='provider@test.com',
            password='testpass123',
            account_type='provider'
        )
        self.client = User.objects.create_user(
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
            price=30.00,
            location='Test Location'
        )

    def test_review_creation(self):
        review = Review.objects.create(
            service=self.service,
            client=self.client,
            provider=self.provider,
            rating=5,
            comment='Excellent service!'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excellent service!')
        self.assertEqual(review.provider, self.provider)

class ServiceAPITest(APITestCase):
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

    def test_service_list(self):
        url = reverse('services:service-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_service_creation_authenticated(self):
        self.client.force_authenticate(user=self.provider)
        url = reverse('services:service-list-create')
        data = {
            'name': 'Test Service',
            'description': 'Test description',
            'price': 50.00,
            'category_id': self.category.id,
            'location': 'Nairobi'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 1)

    def test_service_creation_unauthenticated(self):
        url = reverse('services:service-list-create')
        data = {
            'name': 'Test Service',
            'description': 'Test description',
            'price': 50.00,
            'category_id': self.category.id,
            'location': 'Nairobi'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
