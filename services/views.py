from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Service, Category
from .serializers import ServiceSerializer, CategorySerializer

class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.filter(is_available=True)
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
