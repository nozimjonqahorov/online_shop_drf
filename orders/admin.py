from django.contrib import admin
from .models import Order, OrderItem, Wishlist, Review


admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(Wishlist)