from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile-update'),
    path('list/', views.UserListView.as_view(), name='user-list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('switch-account-type/', views.switch_account_type, name='switch-account-type'),
    path('provider/dashboard/', views.ProviderDashboardView.as_view(), name='provider-dashboard'),
    path('client/dashboard/', views.ClientDashboardView.as_view(), name='client-dashboard'),
    path('business-profile/', views.BusinessProfileView.as_view(), name='business-profile'),
]