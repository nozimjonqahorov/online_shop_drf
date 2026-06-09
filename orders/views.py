from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Wishlist
from products.models import Cart, Product
from .serializers import OrderSerializer, WishlistSerializer, SellerOrderSerializer
from rest_framework.views import APIView
from products.permissions import IsOrdinaryUser, IsOrderSeller
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from .models import PROCESSING
from django.db import transaction
from rest_framework.exceptions import ValidationError




class OrderListCreateGenericView(ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrdinaryUser]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response(
                {"error": "Savatingiz bo'sh! Buyurtma berish uchun mahsulot qo'shing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic(): 
                order = serializer.save(user=request.user)

                
                for item in cart_items:
                    # select_for_update() yordamida Product ni qulflab olamiz.
                    # Bu ayni shu vaqtda boshqa xaridor shu mahsulot zaxirasini o'zgartirishining oldini oladi.
                    product = Product.objects.select_for_update().get(id=item.product.id)
                    
                    if product.stock < item.quantity:
                        raise ValidationError(
                            f"Kechirasiz, '{product.name}' mahsulotidan faqat {product.stock} ta qoldi. "
                        )

                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=product.price,
                        quantity=item.quantity
                    )

                    
                    product.stock -= item.quantity
                    product.save(update_fields=['stock'])


                cart_items.delete()
                
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)


        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class PaymentAPIView(APIView):
 
    permission_classes = [IsAuthenticated, IsOrdinaryUser]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)


        if order.payment_method == "cash":
            return Response(
                {"message": "Siz naqd to'lovni tanlagansiz. To'lov yetkazib berilganda qilinadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.is_paid:
            return Response(
                {"message": "Bu buyurtma uchun allaqachon to'lov qilingan!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.is_paid = True
        order.status = PROCESSING 
        order.save(update_fields=['is_paid', 'status'])

        return Response({
            "message": "To'lov muvaffaqiyatli amalga oshirildi!",
            "order_id": order.id,
            "new_status": order.get_status_display(),
            "is_paid": order.is_paid
        }, status=status.HTTP_200_OK)


class OrderDetailGenericView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    


class WishlistGenericView(RetrieveAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated, IsOrdinaryUser]

    def get_object(self):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist

class WishlistToggleAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOrdinaryUser]

    def post(self, request, product_id):
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)

        if product in wishlist.products.all():
            wishlist.products.remove(product)
            return Response({"message": "Mahsulot sevimlilardan olib tashlandi"}, status=status.HTTP_200_OK)
        else:
            wishlist.products.add(product)
            return Response({"message": "Mahsulot sevimlilarga qo'shildi"}, status=status.HTTP_201_CREATED)
        


class SellerOrderListView(ListAPIView):
    serializer_class = SellerOrderSerializer
    permission_classes = [IsAuthenticated, IsOrderSeller]

    def get_queryset(self):
        return Order.objects.filter(items__product__seller=self.request.user).distinct().order_by('-created_at')


class SellerOrderDetailView(RetrieveUpdateAPIView):
    serializer_class = SellerOrderSerializer
    permission_classes = [IsAuthenticated, IsOrderSeller]
    lookup_field = 'pk' 
    def get_queryset(self):
        return Order.objects.filter(items__product__seller=self.request.user).distinct()
    



# {
#     "email_or_phone":"wblackburn@example.net",
#   "password":"TestPassword123!"
# }