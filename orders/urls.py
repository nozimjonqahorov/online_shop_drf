from django.urls import path
from .views import (
    OrderListCreateGenericView, OrderDetailGenericView, WishlistGenericView, WishlistToggleAPIView )

urlpatterns = [

    path('orders/', OrderListCreateGenericView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailGenericView.as_view(), name='order-detail'),
    path('wishlist/', WishlistGenericView.as_view(), name='wishlist-detail'),
    path('wishlist/toggle/<int:product_id>/', WishlistToggleAPIView.as_view(), name='wishlist-toggle'),
    
]