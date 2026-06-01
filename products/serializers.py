from .models import Product, Category, Cart, CartItem
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.exceptions import ValidationError
from rest_framework import status, serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug'] 

    def validate(self, attrs):
        name = attrs.get("name")

        if name is None:
            return attrs

        name = name.strip()
        if not name:
            raise ValidationError({"message": "Categoriyaga nom kiritilishi shart"})
        if len(name) < 3:
            raise ValidationError({"message": "Categoriya nomi kamida 3-ta harf bo'lishi shart"})
        if not name.isalpha():
            raise ValidationError({"message": "Categoriya nomi faqat harflardan iborat bo'lishi shart"})

        attrs["name"] = name

        return attrs
    

class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.StringRelatedField(read_only=True) 
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 
            'category_name', 'price', 'stock', 'image', 'seller'
        ]
        read_only_fields = ['slug', 'seller']

    

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField(source='total')

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']