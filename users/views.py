from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .serializers import UserRegistrationSerializer, UserProfileSerializer, UserProfileUpdateSerializer, BusinessProfileSerializer
from .permissions import IsProvider, IsClient, IsBusiness, IsOwnerOrAdmin

User = get_user_model()

class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('pages:homepage')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('pages:homepage')

class UserRegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        """Render the registration form"""
        return render(request, 'registration/register.html')

    def post(self, request):
        """Handle registration form submission"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({
                'message': 'Registration successful!',
                'redirect_url': '/'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class UserProfileUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user

class UserListView(generics.ListAPIView):
    """List users by account type"""
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        account_type = self.request.query_params.get('type', None)
        if account_type:
            return User.objects.filter(account_type=account_type)
        return User.objects.all()

class UserDetailView(generics.RetrieveAPIView):
    """Get user profile by ID"""
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def switch_account_type(request):
    """Allow users to switch between account types"""
    user = request.user
    new_account_type = request.data.get('account_type')

    if new_account_type not in ['client', 'provider', 'business']:
        return Response(
            {'error': 'Invalid account type'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if switching to provider/business - might need verification
    if new_account_type in ['provider', 'business'] and user.account_type == 'client':
        # Here you could add verification logic
        pass

    user.account_type = new_account_type
    user.save()

    return Response({
        'message': f'Account type changed to {new_account_type}',
        'account_type': user.account_type
    })

class ProviderDashboardView(APIView):
    """Dashboard view for service providers"""
    permission_classes = (IsProvider,)

    def get(self, request):
        user = request.user

        # Get provider statistics
        services_count = user.services.count()
        orders_count = user.provided_orders.count()
        completed_orders = user.provided_orders.filter(status='completed').count()
        total_earnings = sum(order.total_amount for order in user.provided_orders.filter(status='completed'))

        return Response({
            'services_count': services_count,
            'orders_count': orders_count,
            'completed_orders': completed_orders,
            'total_earnings': total_earnings,
            'recent_orders': UserProfileSerializer(user.provided_orders.all()[:5], many=True).data
        })

class ClientDashboardView(APIView):
    """Dashboard view for clients"""
    permission_classes = (IsClient,)

    def get(self, request):
        user = request.user

        # Get client statistics
        orders_count = user.orders.count()
        completed_orders = user.orders.filter(status='completed').count()
        total_spent = sum(order.total_amount for order in user.orders.filter(status='completed'))

        return Response({
            'orders_count': orders_count,
            'completed_orders': completed_orders,
            'total_spent': total_spent,
            'recent_orders': UserProfileSerializer(user.orders.all()[:5], many=True).data
        })

class BusinessProfileView(generics.RetrieveUpdateAPIView):
    """View for managing business profiles"""
    serializer_class = BusinessProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user.business_profile

    def get_queryset(self):
        return BusinessProfile.objects.filter(user=self.request.user)
