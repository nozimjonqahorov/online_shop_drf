from .models import Product, Category, Cart, CartItem
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.exceptions import ValidationError
from rest_framework import status, serializers
from orders.models import Review


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
    reviews = serializers.SlugRelatedField(
        many=True, 
        read_only=True, 
        slug_field='content'
    )
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 
            'category_name', 'price', 'stock', 'image', 'seller', 'reviews'
        ]
        read_only_fields = ['slug', 'seller']

    

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    subtotal = serializers.ReadOnlyField()
    
    quantity = serializers.IntegerField(min_value=1, default=1)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']

    def create(self, validated_data):
        request = self.context.get('request')
        product = validated_data['product']
        requested_quantity = validated_data['quantity']
    

        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        
        existing_cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        
        # Agar savatda bo'lsa uning sonini olamiz, yo'q bo'lsa 0 deb hisoblaymiz
        current_quantity_in_cart = existing_cart_item.quantity if existing_cart_item else 0
        
        # Savatdagi jami bo'ladigan miqdorni hisoblaymiz
        total_quantity_after_add = current_quantity_in_cart + requested_quantity

        # JAMI miqdorni bazadagi zaxira bilan solishtiramiz
        if product.stock < total_quantity_after_add:
            available_to_add = product.stock - current_quantity_in_cart
            
            if available_to_add > 0:
                raise ValidationError({
                    "message": f"Savatda allaqachon {current_quantity_in_cart} ta bor. Yana faqat {available_to_add} ta qo'sha olasiz (Jami zaxira: {product.stock})."
                })
            else:
                raise ValidationError({
                    "message": f"Siz bu mahsulotning barcha zaxirasini savatga qo'shib bo'lgansiz."
                })
        
        
        if existing_cart_item:
            existing_cart_item.quantity += requested_quantity
            existing_cart_item.save()
            return existing_cart_item
        else:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=requested_quantity)
            return cart_item

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField(source='total')

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']



class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'user_username', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        product = attrs.get('product')

        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError(
                {"error": "Siz ushbu mahsulotga oldin izoh qoldirgansiz! Bir marta yozish mumkin."}
            )
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)