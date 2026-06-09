from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.models import ORDINARY_USER, SELLER, ADMIN


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.user_role == SELLER
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_role == ADMIN)
        )


class IsSellerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.user_role in (SELLER, ADMIN)
        )


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.user_role == ADMIN:
            return True
        return getattr(obj, "user", None) == request.user or getattr(obj, "seller", None) == request.user


class IsOwnerOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff or request.user.user_role == ADMIN:
            return True
        return getattr(obj, "seller", None) == request.user
    


class IsOrdinaryUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_role  == ORDINARY_USER
    

class IsOrderSeller(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_role == SELLER

    def has_object_permission(self, request, view, obj):
        return obj.items.filter(product__seller=request.user).exists()