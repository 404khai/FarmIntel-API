# core/permissions.py
from rest_framework.permissions import BasePermission

class IsFarmer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "FARMER"

class IsCooperative(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "COOPERATIVE"

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"
