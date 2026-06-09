from django.shortcuts import render, get_object_or_404 
from .models import Product, Category, CartItem, Cart
from orders.models import Review
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import CategorySerializer, ProductSerializer, CartItemSerializer, CartSerializer
from .permissions import IsAdmin, IsSellerOrAdmin, IsOwnerOrAdminOrReadOnly, IsSeller, IsOrdinaryUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import ReviewSerializer



class CategoryListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()] 
        return [AllowAny()]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdmin()] 
        return [AllowAny()]

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        serializer = CategorySerializer(category, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        category.delete()
        return Response(
            {"message": "Kategoriya muvaffaqiyatli o'chirildi."}, 
            status=status.HTTP_204_NO_CONTENT
        )
  

class ProductListAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSeller()]
        return [AllowAny()]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def get_object(self, slug):
        product = get_object_or_404(Product, slug=slug)
        self.check_object_permissions(self.request, product)
        return product

    def get(self, request, slug):
        product = self.get_object(slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, slug):
        product = self.get_object(slug)
        serializer = ProductSerializer(product, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, slug):
        product = self.get_object(slug)
        product.delete()
        return Response(
            {"message": "Mahsulot muvaffaqiyatli o'chirildi."}, 
            status=status.HTTP_204_NO_CONTENT
        )
    

class CartDetailView(RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsOrdinaryUser]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemCreateView(CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, IsOrdinaryUser]


class CartItemDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)


class ReviewCreateAPIView(CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsOrdinaryUser] 