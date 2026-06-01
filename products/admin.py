from django.contrib import admin
from .models import Category, Cart, CartItem, Product


admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Product)
admin.site.register(Category)