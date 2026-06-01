from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from shared.models import BaseModel
from accounts.models import CustomUser
from products.models import Product
from django.db.models import Sum, F



PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED = (
    "pending", "processing", "shipped", "delivered", "cancelled"
)


class Order(BaseModel):
    STATUS_CHOICES = (
        (PENDING,    "Kutilmoqda"),
        (PROCESSING, "Tayyorlanmoqda"),
        (SHIPPED,    "Yo'lda"),
        (DELIVERED,  "Yetkazildi"),
        (CANCELLED,  "Bekor qilindi"),
    )

    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=PENDING
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=13)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Buyurtma #{self.pk} — {self.status}"


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.price * self.quantity

    def update_order_total(self):
        total_sum = self.order.items.aggregate(
            total_sum=Sum(F('price') * F('quantity'))
        )['total_sum'] or 0
        
        self.order.total = total_sum
        self.order.save(update_fields=['total'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_order_total()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_order_total()



class Review(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reviews")
    content = models.TextField(blank=True)

    class Meta:
        unique_together = ("product", "user")  

    def __str__(self):
        return f"{self.user.username} — {self.product.name}"


class Wishlist(BaseModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="wishlist")
    products = models.ManyToManyField(Product,  blank=True)

    def __str__(self):
        return f"{self.user.username} sevimlilar"