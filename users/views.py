from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic import View, CreateView, UpdateView, DetailView
from django.contrib.auth.forms import AuthenticationForm
from rest_framework import generics, permissions
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView as AuthLoginView
from .forms import UserRegistrationForm, ProfileCreationForm, UserProfileUpdateForm, CustomLoginForm
from .serializers import UserSerializer  # Add this import
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginView(AuthLoginView):
    template_name = 'users/login.html'
    form_class = CustomLoginForm
    success_url = reverse_lazy('home')
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.success_url

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please login to continue.')
        return response

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile_update.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number', 'bio', 'profile_picture']
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully!')
        return response

class ProfileCreateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileCreationForm
    template_name = 'users/profile_create.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.calculate_profile_completion()
        messages.success(self.request, 'Profile created successfully!')
        return response
