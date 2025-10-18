from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsProvider(BasePermission):
    """Permission for service providers and businesses"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.account_type in ['provider', 'business']

class IsClient(BasePermission):
    """Permission for clients"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.account_type == 'client'

class IsBusiness(BasePermission):
    """Permission for businesses only"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.account_type == 'business'

class CanManageService(BasePermission):
    """Permission to manage a specific service (provider or business)"""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj.provider == request.user

class CanManageOrder(BasePermission):
    """Permission to manage a specific order (client or provider)"""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj.client == request.user or obj.provider == request.user

class IsOwnerOrAdmin(BasePermission):
    """Permission for object owners or admin users"""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj == request.user or request.user.is_staff