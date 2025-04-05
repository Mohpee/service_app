from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderSerializer

class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user)

class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
