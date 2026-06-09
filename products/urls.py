from django.urls import path
from .views import CategoryListAPIView, CategoryDetailAPIView, ProductListAPIView, ProductDetailAPIView, CartDetailView, CartItemDetailView, CartItemCreateView, ReviewCreateAPIView    

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/review/', ReviewCreateAPIView.as_view(), name='review-create'),
    path('products/<slug:slug>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/', CartItemCreateView.as_view(), name='cart-item-add'),
    path('cart/item/<uuid:pk>/', CartItemDetailView.as_view(), name='cart-item-detail'),
    
]