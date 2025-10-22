from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Template views (for web interface)
    path('', views.services_list, name='service-list'),
    path('list/', views.ServiceListView.as_view(), name='service-list-api'),

    # API views (for JSON responses)
    path('api/', views.ServiceListCreateView.as_view(), name='service-list-create'),
    path('api/<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),
    path('api/search/', views.ServiceSearchView.as_view(), name='service-search'),
    path('api/search/advanced/', views.AdvancedSearchView.as_view(), name='advanced-search'),
    path('api/search/suggestions/', views.SearchSuggestionsView.as_view(), name='search-suggestions'),
    path('api/recommendations/', views.ServiceRecommendationsView.as_view(), name='service-recommendations'),
    path('api/nearby/', views.NearbyServicesView.as_view(), name='nearby-services'),
    path('api/provider/<int:provider_id>/', views.ProviderServicesView.as_view(), name='provider-services'),
    path('api/categories/', views.CategoryListView.as_view(), name='category-list'),
    path('api/categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('api/packages/', views.ServicePackageListCreateView.as_view(), name='service-packages'),
    path('api/favorites/', views.FavoriteServiceView.as_view(), name='favorite-services'),
    path('api/favorites/<int:service_id>/', views.FavoriteServiceView.as_view(), name='favorite-service'),
    path('api/schedule/', views.ProviderScheduleView.as_view(), name='provider-schedule'),
    path('api/promotions/', views.PromotionListView.as_view(), name='promotions'),
]