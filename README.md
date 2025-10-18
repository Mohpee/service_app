# Service Marketplace App

A comprehensive service marketplace application built with Django REST Framework that connects service providers with clients. The platform supports multiple user roles, payment integration, real-time notifications, and advanced search functionality.

## Features

### Core Features
- **Multi-role User System**: Clients, Service Providers, and Businesses
- **Service Management**: Create, update, and manage services with categories
- **Booking System**: Advanced booking with scheduling and status tracking
- **Payment Integration**: M-Pesa and Stripe payment processing
- **Real-time Notifications**: Instant notifications for orders, payments, and updates
- **Advanced Search**: Filter by location, price, rating, availability, and more
- **Review System**: Rating and review system for services
- **Admin Dashboard**: Comprehensive admin interface for platform management

### Technical Features
- **RESTful API**: Complete API with JWT authentication
- **Role-based Permissions**: Custom permissions for different user types
- **Docker Support**: Containerized deployment with Docker Compose
- **Database Support**: PostgreSQL with Redis caching
- **File Upload**: Image upload for services and profiles
- **Email Integration**: SMTP email configuration
- **CORS Support**: Cross-origin resource sharing for frontend integration

## Technology Stack

- **Backend**: Django 5.2, Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Payments**: M-Pesa (Safaricom), Stripe
- **Authentication**: JWT tokens
- **Deployment**: Docker, Nginx, Gunicorn
- **File Storage**: AWS S3 (production) / Local (development)

## Installation

### Prerequisites
- Python 3.13+
- PostgreSQL
- Redis
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd service_app
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Environment Configuration

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/service_app

# Redis
REDIS_URL=redis://localhost:6379/1

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payments
STRIPE_PUBLIC_KEY=pk_test_your_stripe_key
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# M-Pesa
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_SHORTCODE=your_shortcode
MPESA_PASSKEY=your_passkey
```

## Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations in container**
   ```bash
   docker-compose exec app python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec app python manage.py createsuperuser
   ```

## API Documentation

### Authentication Endpoints
- `POST /api/users/register/` - User registration
- `POST /api/token/` - JWT token obtain
- `POST /api/token/refresh/` - JWT token refresh

### User Management
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/update/` - Update user profile
- `GET /api/users/provider/dashboard/` - Provider dashboard
- `GET /api/users/client/dashboard/` - Client dashboard

### Services
- `GET /api/services/` - List services (with filtering)
- `POST /api/services/` - Create service (providers only)
- `GET /api/services/search/` - Search services
- `GET /api/services/search/advanced/` - Advanced search
- `GET /api/services/nearby/` - Find nearby services

### Orders & Bookings
- `GET /api/orders/` - List orders
- `POST /api/orders/` - Create order
- `POST /api/orders/book/{service_id}/` - Book a service
- `PUT /api/orders/{id}/update-status/` - Update order status

### Payments
- `POST /api/payments/create/{order_id}/` - Create payment
- `GET /api/payments/history/` - Payment history
- `POST /api/payments/{payment_id}/refund/` - Process refund

### Notifications
- `GET /api/orders/notifications/` - List notifications
- `PUT /api/orders/notifications/{id}/` - Mark as read
- `GET /api/orders/notifications/unread-count/` - Unread count

## User Roles

### Client
- Browse and search services
- Book services
- Make payments
- Leave reviews
- Receive notifications

### Service Provider
- Create and manage services
- Receive bookings
- Update order status
- Receive payments
- View earnings

### Business
- All provider features
- Multiple service categories
- Business analytics

## Testing

Run the test suite:
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test services
python manage.py test orders

# Run with coverage
coverage run manage.py test
coverage report
```

## Deployment

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up SSL certificates
- [ ] Configure static files storage (AWS S3)
- [ ] Set up email backend
- [ ] Configure payment webhooks
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Using Docker Compose (Production)
```bash
# Update environment variables in docker-compose.yml
docker-compose -f docker-compose.prod.yml up -d
```

## API Usage Examples

### Register a new user
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword",
    "password2": "securepassword",
    "first_name": "John",
    "last_name": "Doe",
    "account_type": "client"
  }'
```

### Search services
```bash
curl "http://localhost:8000/api/services/search/?q=cleaning&location=nairobi&min_rating=4"
```

### Create a service (Provider only)
```bash
curl -X POST http://localhost:8000/api/services/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "House Cleaning",
    "description": "Professional house cleaning service",
    "price": 50.00,
    "category_id": 1,
    "location": "Nairobi, Kenya"
  }'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team

## Changelog

### Version 1.0.0
- Initial release
- Core marketplace functionality
- Payment integration
- User role management
- Admin dashboard
