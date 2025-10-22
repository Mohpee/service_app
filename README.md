# ServiceHub - Service Marketplace Platform

A comprehensive Django-based platform that connects service providers with clients, enabling seamless booking, payment processing, and service management.

## 🚀 Features

### Core Functionality
- **Multi-role User System**: Clients, Individual Providers, and Business accounts
- **Service Management**: Create, update, and manage service listings with rich details
- **Advanced Search & Filtering**: Find services by location, category, price, rating, and more
- **Booking System**: Schedule and manage service appointments
- **Payment Integration**: Support for M-Pesa and Stripe payments
- **Review & Rating System**: Build trust with verified reviews
- **Real-time Notifications**: Stay updated with booking and payment notifications
- **Admin Dashboard**: Comprehensive management interface

### Technical Features
- **RESTful API**: Complete API for mobile and web integrations
- **Real-time Updates**: WebSocket support for live notifications
- **Payment Processing**: Secure M-Pesa and Stripe integration
- **Location Services**: GPS-based service discovery
- **File Uploads**: Image and document management
- **Caching**: Redis-powered performance optimization
- **Background Tasks**: Celery for async processing

## 🛠️ Tech Stack

- **Backend**: Django 5.2, Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Cache**: Redis
- **Task Queue**: Celery
- **Payments**: M-Pesa (Daraja), Stripe
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Deployment**: Docker, Nginx, Gunicorn
- **Monitoring**: Sentry (error tracking)

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (for containerized deployment)

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/servicehub.git
   cd servicehub
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

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
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

### Production Deployment

1. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Manual deployment**
   ```bash
   # Install production dependencies
   pip install gunicorn psycopg2-binary

   # Collect static files
   python manage.py collectstatic

   # Run with Gunicorn
   gunicorn service_app.wsgi:application --bind 0.0.0.0:8000
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/servicehub

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# Celery
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1

# Payment Gateways
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest orders/tests.py

# Run Django's test runner
python manage.py test
```

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/users/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Service Endpoints
- `GET /api/services/` - List services with filtering
- `POST /api/services/` - Create new service (providers only)
- `GET /api/services/{id}/` - Service details
- `GET /api/services/search/` - Advanced search
- `GET /api/services/recommendations/` - Personalized recommendations

### Order Endpoints
- `GET /api/orders/` - List user orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/{id}/` - Order details
- `POST /api/orders/book/{service_id}/` - Quick booking

### Payment Endpoints
- `POST /api/payments/create/{order_id}/` - Initiate payment
- `GET /api/payments/history/` - Payment history
- `POST /api/payments/{payment_id}/refund/` - Process refund

## 🔒 Security Features

- JWT authentication with refresh tokens
- Role-based access control (RBAC)
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure file uploads
- Rate limiting
- Audit logging

## 📈 Performance Optimization

- Database query optimization
- Redis caching for frequently accessed data
- Static file optimization with WhiteNoise
- Gzip compression
- Database indexing
- Background task processing with Celery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, email support@servicehub.com or join our Slack community.

## 🙏 Acknowledgments

- Django community for the excellent framework
- All contributors and users of this platform
- Open source libraries that made this possible

---

**Made with ❤️ by the ServiceHub Team**
