from rest_framework import serializers
from .models import Order, OrderItem, Wishlist
from products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField() 

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'address','payment_method', 'is_paid', 'phone', 'note', 'items']
        read_only_fields = ['status', 'total', 'is_paid']


class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    products = ProductSerializer(many=True, read_only=True) 

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products']



class SellerOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'subtotal']


class SellerOrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'address', 'phone', 'note', 'items', 'created_at']
        read_only_fields = ['id', 'user', 'total', 'address', 'phone', 'note', 'created_at']

    def get_items(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            seller_items = obj.items.filter(product__seller=request.user)
            return SellerOrderItemSerializer(seller_items, many=True).data
        return []