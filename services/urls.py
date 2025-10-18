from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.ServiceListCreateView.as_view(), name='service-list-create'),
    path('<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),
    path('search/', views.ServiceSearchView.as_view(), name='service-search'),
    path('search/advanced/', views.AdvancedSearchView.as_view(), name='advanced-search'),
    path('search/suggestions/', views.SearchSuggestionsView.as_view(), name='search-suggestions'),
    path('recommendations/', views.ServiceRecommendationsView.as_view(), name='service-recommendations'),
    path('nearby/', views.NearbyServicesView.as_view(), name='nearby-services'),
    path('provider/<int:provider_id>/', views.ProviderServicesView.as_view(), name='provider-services'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('packages/', views.ServicePackageListCreateView.as_view(), name='service-packages'),
    path('favorites/', views.FavoriteServiceView.as_view(), name='favorite-services'),
    path('favorites/<int:service_id>/', views.FavoriteServiceView.as_view(), name='favorite-service'),
    path('schedule/', views.ProviderScheduleView.as_view(), name='provider-schedule'),
    path('promotions/', views.PromotionListView.as_view(), name='promotions'),
]