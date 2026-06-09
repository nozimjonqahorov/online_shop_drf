from django.urls import path
from .views import (
    OrderListCreateGenericView, OrderDetailGenericView, WishlistGenericView, WishlistToggleAPIView, SellerOrderDetailView, SellerOrderListView, PaymentAPIView)

urlpatterns = [

    path('orders/', OrderListCreateGenericView.as_view(), name='order-list-create'),
    path('orders/<uuid:pk>/pay/', PaymentAPIView.as_view(), name='order-pay'),
    path('orders/<uuid:pk>/', OrderDetailGenericView.as_view(), name='order-detail'),
    path('seller/orders/', SellerOrderListView.as_view(), name='seller-order-list'),
    path('seller/orders/<uuid:pk>/', SellerOrderDetailView.as_view(), name='seller-order-detail'),
    path('wishlist/', WishlistGenericView.as_view(), name='wishlist-detail'),
    path('wishlist/toggle/<uuid:product_id>/', WishlistToggleAPIView.as_view(), name='wishlist-toggle'),
    
]