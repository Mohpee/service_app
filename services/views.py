from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.renderers import JSONRenderer
from .models import Service, Category, ServicePackage, FavoriteService, ProviderSchedule, Promotion
from .serializers import ServiceSerializer, CategorySerializer, ServicePackageSerializer, FavoriteServiceSerializer, ProviderScheduleSerializer, PromotionSerializer
from users.permissions import IsProvider, CanManageService

class ServiceListView(generics.ListAPIView):
    """List services for web interface"""
    queryset = Service.objects.filter(is_available=True)
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'location', 'is_available']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['price', 'rating', 'created_at', 'total_bookings']
    ordering = ['-rating', '-created_at']

    def get_queryset(self):
        queryset = Service.objects.filter(is_available=True)

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by rating
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)

        # Filter by provider type
        provider_type = self.request.query_params.get('provider_type')
        if provider_type:
            queryset = queryset.filter(provider__account_type=provider_type)

        return queryset

def services_list(request):
    """Template view for services list page"""
    from django.core.paginator import Paginator

    # Get services with filters
    services = Service.objects.filter(is_available=True).order_by('-rating', '-created_at')

    # Apply filters from request
    category = request.GET.get('category')
    location = request.GET.get('location')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_rating = request.GET.get('min_rating')
    sort_by = request.GET.get('sort_by', 'relevance')

    if category:
        # Filter by category name instead of ID
        services = services.filter(category__name__iexact=category)
    if location:
        services = services.filter(location__icontains=location)
    if min_price:
        services = services.filter(price__gte=min_price)
    if max_price:
        services = services.filter(price__lte=max_price)
    if min_rating:
        services = services.filter(rating__gte=min_rating)

    # Apply sorting
    if sort_by == 'price_low':
        services = services.order_by('price')
    elif sort_by == 'price_high':
        services = services.order_by('-price')
    elif sort_by == 'rating':
        services = services.order_by('-rating')
    elif sort_by == 'newest':
        services = services.order_by('-created_at')
    elif sort_by == 'popular':
        services = services.order_by('-total_bookings')
    # else: relevance (default ordering)

    # Pagination
    paginator = Paginator(services, 12)  # 12 services per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get categories for filter
    from .models import Category
    categories = Category.objects.all()

    context = {
        'services': page_obj,
        'categories': categories,
        'request': request,
    }

    return render(request, 'services/service_list.html', context)

class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.filter(is_available=True)
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'location', 'is_available']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['price', 'rating', 'created_at', 'total_bookings']
    ordering = ['-rating', '-created_at']
    renderer_classes = [JSONRenderer]  # Force JSON response only

    def get_queryset(self):
        queryset = Service.objects.filter(is_available=True)

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by rating
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)

        # Filter by provider type
        provider_type = self.request.query_params.get('provider_type')
        if provider_type:
            queryset = queryset.filter(provider__account_type=provider_type)
    
        return queryset
    
    def services_list(request):
        """Template view for services list page"""
        from django.core.paginator import Paginator
    
        # Get services with filters
        services = Service.objects.filter(is_available=True).order_by('-rating', '-created_at')
    
        # Apply filters from request
        category = request.GET.get('category')
        location = request.GET.get('location')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        min_rating = request.GET.get('min_rating')
        sort_by = request.GET.get('sort_by', 'relevance')
    
        if category:
            # Filter by category name instead of ID
            services = services.filter(category__name__iexact=category)
    
        if location:
            services = services.filter(location__icontains=location)
        if min_price:
            services = services.filter(price__gte=min_price)
        if max_price:
            services = services.filter(price__lte=max_price)
        if min_rating:
            services = services.filter(rating__gte=min_rating)
    
        # Apply sorting
        if sort_by == 'price_low':
            services = services.order_by('price')
        elif sort_by == 'price_high':
            services = services.order_by('-price')
        elif sort_by == 'rating':
            services = services.order_by('-rating')
        elif sort_by == 'newest':
            services = services.order_by('-created_at')
        elif sort_by == 'popular':
            services = services.order_by('-total_bookings')
        # else: relevance (default ordering)
    
        # Pagination
        paginator = Paginator(services, 12)  # 12 services per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    
        # Get categories for filter
        from .models import Category
        categories = Category.objects.all()
    
        context = {
            'services': page_obj,
            'categories': categories,
            'request': request,
        }
    
        return render(request, 'services/service_list.html', context)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)

class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [CanManageService()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get(self, request, *args, **kwargs):
        # Check if this is an API request (JSON format)
        if request.accepted_renderer.format == 'json' or 'format=json' in request.GET.get('format', ''):
            return super().get(request, *args, **kwargs)

        # Otherwise, render HTML template
        service = self.get_object()
        return render(request, 'services/service_detail.html', {'service': service})

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    renderer_classes = [JSONRenderer]  # Force JSON response only

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    renderer_classes = [JSONRenderer]  # Force JSON response only

class ServiceSearchView(APIView):
    """Advanced service search with multiple filters"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    renderer_classes = [JSONRenderer]  # Force JSON response only

    def get(self, request):
        query = request.query_params.get('q', '')
        category = request.query_params.get('category')
        location = request.query_params.get('location')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        min_rating = request.query_params.get('min_rating')

        services = Service.objects.filter(is_available=True)

        if query:
            services = services.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query)
            )

        if category:
            # Filter by category name instead of ID
            services = services.filter(category__name__iexact=category)

        if location:
            services = services.filter(location__icontains=location)

        if min_price:
            services = services.filter(price__gte=min_price)

        if max_price:
            services = services.filter(price__lte=max_price)

        if min_rating:
            services = services.filter(rating__gte=min_rating)

        # Order by rating and relevance
        services = services.order_by('-rating', '-total_bookings')

        serializer = ServiceSerializer(services, many=True, context={'request': request})
        return Response(serializer.data)

class ProviderServicesView(generics.ListAPIView):
    """List services by a specific provider"""
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]  # Force JSON response only

    def get_queryset(self):
        provider_id = self.kwargs['provider_id']
        return Service.objects.filter(provider_id=provider_id, is_available=True)

class NearbyServicesView(APIView):
    """Find services near a location"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    renderer_classes = [JSONRenderer]  # Force JSON response only

    def get(self, request):
        latitude = request.query_params.get('lat')
        longitude = request.query_params.get('lng')
        radius = request.query_params.get('radius', 10)  # km

        if not latitude or not longitude:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Simple distance calculation (you might want to use a proper GIS library)
        services = Service.objects.filter(
            is_available=True,
            latitude__isnull=False,
            longitude__isnull=False
        )

        # For demo purposes, just return services with location data
        # In production, implement proper distance calculation
        serializer = ServiceSerializer(services[:20], many=True, context={'request': request})
        return Response(serializer.data)

class ServicePackageListCreateView(generics.ListCreateAPIView):
    """List and create service packages"""
    serializer_class = ServicePackageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    renderer_classes = [JSONRenderer]  # Force JSON response only

    def get_queryset(self):
        service_id = self.request.query_params.get('service')
        if service_id:
            return ServicePackage.objects.filter(service_id=service_id, is_active=True)
        return ServicePackage.objects.filter(is_active=True)

    def perform_create(self, serializer):
        service = serializer.validated_data['service']
        if service.provider != self.request.user:
            raise permissions.PermissionDenied("You can only create packages for your own services")
        serializer.save()

class FavoriteServiceView(APIView):
    """Add/remove favorite services"""
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]  # Force JSON response only

    def post(self, request, service_id):
        from .models import Service
        try:
            service = Service.objects.get(id=service_id, is_available=True)
        except Service.DoesNotExist:
            return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = FavoriteService.objects.get_or_create(
            user=request.user,
            service=service
        )

        if not created:
            favorite.delete()
            return Response({'message': 'Removed from favorites'})

        serializer = FavoriteServiceSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        """Get user's favorite services"""
        favorites = FavoriteService.objects.filter(user=request.user)
        serializer = FavoriteServiceSerializer(favorites, many=True)
        return Response(serializer.data)

class ProviderScheduleView(generics.ListCreateAPIView):
    """Manage provider schedules"""
    serializer_class = ProviderScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]  # Force JSON response only

    def get_queryset(self):
        return ProviderSchedule.objects.filter(provider=self.request.user)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)

class PromotionListView(generics.ListCreateAPIView):
    """List and create promotions"""
    serializer_class = PromotionSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]  # Force JSON response only

    def get_queryset(self):
        user = self.request.user
        if user.account_type == 'business':
            return Promotion.objects.filter(provider=user)
        return Promotion.objects.filter(is_active=True)

    def perform_create(self, serializer):
        if self.request.user.account_type == 'business':
            serializer.save(provider=self.request.user)
        else:
            raise permissions.PermissionDenied("Only business accounts can create promotions")

class AdvancedSearchView(APIView):
    """Advanced search with multiple criteria"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    renderer_classes = [JSONRenderer]  # Force JSON response only

    def get(self, request):
        # Get all search parameters
        query = request.query_params.get('q', '')
        category = request.query_params.get('category')
        subcategory = request.query_params.get('subcategory')
        location = request.query_params.get('location')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        min_rating = request.query_params.get('min_rating')
        availability = request.query_params.get('availability')
        experience_min = request.query_params.get('experience_min')
        languages = request.query_params.get('languages')
        sort_by = request.query_params.get('sort_by', 'relevance')

        services = Service.objects.filter(is_available=True)

        # Text search
        if query:
            services = services.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(provider__first_name__icontains=query) |
                Q(provider__last_name__icontains=query)
            )

        # Category filter
        if category:
            # Filter by category name instead of ID
            services = services.filter(category__name__iexact=category)

        # Location filter
        if location:
            services = services.filter(location__icontains=location)

        # Price range filter
        if min_price:
            services = services.filter(price__gte=min_price)
        if max_price:
            services = services.filter(price__lte=max_price)

        # Rating filter
        if min_rating:
            services = services.filter(rating__gte=min_rating)

        # Availability filter
        if availability:
            if availability == 'today':
                # Filter services available today
                services = services.filter(availability_type__in=['ALWAYS', 'WEEKDAY'])
            elif availability == 'weekend':
                services = services.filter(availability_type__in=['ALWAYS', 'WEEKEND'])

        # Experience filter
        if experience_min:
            services = services.filter(experience_years__gte=experience_min)

        # Languages filter
        if languages:
            language_list = languages.split(',')
            services = services.filter(languages__overlap=language_list)

        # Sorting
        if sort_by == 'price_low':
            services = services.order_by('price')
        elif sort_by == 'price_high':
            services = services.order_by('-price')
        elif sort_by == 'rating':
            services = services.order_by('-rating')
        elif sort_by == 'newest':
            services = services.order_by('-created_at')
        elif sort_by == 'popular':
            services = services.order_by('-total_bookings')
        else:  # relevance
            services = services.order_by('-rating', '-total_bookings')

        # Get pagination parameters
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        start = (page - 1) * per_page
        end = start + per_page

        # Paginate results
        total_count = services.count()
        services_page = services[start:end]

        serializer = ServiceSerializer(services_page, many=True, context={'request': request})

        return Response({
            'results': serializer.data,
            'total_count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        })

class SearchSuggestionsView(APIView):
    """Get search suggestions and popular searches"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    renderer_classes = [JSONRenderer]  # Force JSON response only

    def get(self, request):
        query = request.query_params.get('q', '')

        suggestions = {
            'services': [],
            'locations': [],
            'categories': [],
            'providers': []
        }

        if query:
            # Service name suggestions
            service_suggestions = Service.objects.filter(
                name__icontains=query,
                is_available=True
            ).values('name')[:5]
            suggestions['services'] = [s['name'] for s in service_suggestions]

            # Location suggestions
            location_suggestions = Service.objects.filter(
                location__icontains=query,
                is_available=True
            ).values('location')[:5]
            suggestions['locations'] = list(set([s['location'] for s in location_suggestions]))

            # Provider suggestions
            provider_suggestions = Service.objects.filter(
                Q(provider__first_name__icontains=query) |
                Q(provider__last_name__icontains=query),
                is_available=True
            ).values('provider__first_name', 'provider__last_name')[:5]
            suggestions['providers'] = [
                f"{p['provider__first_name']} {p['provider__last_name']}"
                for p in provider_suggestions
            ]

        # Category suggestions (always show popular categories)
        popular_categories = Category.objects.all().values('name')[:8]
        suggestions['categories'] = [c['name'] for c in popular_categories]

        return Response(suggestions)

class ServiceRecommendationsView(APIView):
    """Get personalized service recommendations"""
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer]  # Force JSON response only

    def get(self, request):
        user = request.user

        # Get user's order history to find preferences
        user_orders = Order.objects.filter(client=user, status='completed')
        preferred_categories = user_orders.values('service__category').annotate(
            count=Count('id')
        ).order_by('-count')[:3]

        recommendations = Service.objects.filter(is_available=True)

        if preferred_categories:
            # Recommend services from preferred categories
            category_ids = [cat['service__category'] for cat in preferred_categories]
            recommendations = recommendations.filter(category_id__in=category_ids)

        # Also recommend highly rated services
        recommendations = recommendations.filter(rating__gte=4.0)

        # Exclude services user already ordered
        ordered_service_ids = user_orders.values('service_id')
        recommendations = recommendations.exclude(id__in=ordered_service_ids)

        # Order by rating and limit results
        recommendations = recommendations.order_by('-rating')[:10]

        serializer = ServiceSerializer(recommendations, many=True, context={'request': request})
        return Response(serializer.data)
