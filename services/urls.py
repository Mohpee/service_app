from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.ServiceListCreateView.as_view(), name='service-list-create'),
    path('<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
]