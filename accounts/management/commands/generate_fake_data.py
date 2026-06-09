from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
import random
from decimal import Decimal

from accounts.models import CustomUser, ORDINARY_USER, SELLER, VIA_EMAIL, VIA_PHONE, DONE
from products.models import Category, Product, Cart
from orders.models import Order, OrderItem, Review, Wishlist, PENDING, PROCESSING, SHIPPED, DELIVERED


class Command(BaseCommand):
    help = "Generate fake data for development and testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=20,
            help="Number of users to create"
        )
        parser.add_argument(
            "--sellers",
            type=int,
            default=5,
            help="Number of sellers to create"
        )
        parser.add_argument(
            "--categories",
            type=int,
            default=10,
            help="Number of categories to create"
        )
        parser.add_argument(
            "--products",
            type=int,
            default=50,
            help="Number of products to create"
        )
        parser.add_argument(
            "--orders",
            type=int,
            default=30,
            help="Number of orders to create"
        )

    def handle(self, *args, **options):
        fake = Faker()
        
        users_count = options["users"]
        sellers_count = options["sellers"]
        categories_count = options["categories"]
        products_count = options["products"]
        orders_count = options["orders"]

        self.stdout.write(self.style.SUCCESS("🚀 Starting fake data generation..."))

        # Generate Ordinary Users
        self.stdout.write("📝 Generating ordinary users...")
        users = []
        for i in range(users_count):
            try:
                email = fake.email()
                phone = f"+998{random.randint(90, 99)}{random.randint(1000000, 9999999)}"
                
                user = CustomUser.objects.create_user(
                    username=fake.user_name()[:30],
                    email=email,
                    phone_number=phone,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    password="TestPassword123!",
                    user_role=ORDINARY_USER,
                    auth_type=random.choice([VIA_EMAIL, VIA_PHONE]),
                    auth_status=DONE
                )
                users.append(user)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Error creating user: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(users)} ordinary users"))

        # Generate Sellers
        self.stdout.write("📝 Generating sellers...")
        sellers = []
        for i in range(sellers_count):
            try:
                email = fake.email()
                phone = f"+998{random.randint(90, 99)}{random.randint(1000000, 9999999)}"
                
                seller = CustomUser.objects.create_user(
                    username=fake.user_name()[:30],
                    email=email,
                    phone_number=phone,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    password="TestPassword123!",
                    user_role=SELLER,
                    auth_type=random.choice([VIA_EMAIL, VIA_PHONE]),
                    auth_status=DONE
                )
                sellers.append(seller)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Error creating seller: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(sellers)} sellers"))

        # Generate Categories
        self.stdout.write("📝 Generating categories...")
        categories = []
        category_names = [
            "Electronics", "Clothing", "Books", "Home & Garden",
            "Sports", "Toys", "Beauty", "Food", "Furniture", "Art"
        ]
        
        for name in category_names[:categories_count]:
            try:
                category = Category.objects.create(name=name)
                categories.append(category)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Error creating category: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(categories)} categories"))

        # Generate Products
        self.stdout.write("📝 Generating products...")
        products = []
        for i in range(products_count):
            try:
                product = Product.objects.create(
                    name=fake.word().capitalize() + " " + fake.word().capitalize(),
                    description=fake.paragraph(nb_sentences=5),
                    category=random.choice(categories),
                    price=Decimal(str(round(random.uniform(10, 1000), 2))),
                    stock=random.randint(0, 100),
                    seller=random.choice(sellers)
                )
                products.append(product)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Error creating product: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(products)} products"))

        # Create Carts for all users
        self.stdout.write("📝 Generating shopping carts...")
        for user in users:
            try:
                Cart.objects.get_or_create(user=user)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Error creating cart: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"✓ Created carts for all users"))

        # Generate Orders
        self.stdout.write("📝 Generating orders...")
        statuses = [PENDING, PROCESSING, SHIPPED, DELIVERED]
        for i in range(orders_count):
            try:
                user = random.choice(users)
                order = Order.objects.create(
                    user=user,
                    status=random.choice(statuses),
                    address=fake.address().replace("\n", ", "),
                    phone=f"+998{random.randint(90, 99)}{random.randint(1000000, 9999999)}",
                    note=fake.sentence() if random.random() > 0.7 else ""
                )
                
                # Add items to order
                num_items = random.randint(1, 5)
                for _ in range(num_items):
                    product = random.choice(products)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=product.price,
                        quantity=random.randint(1, 3)
                    )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Error creating order: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"✓ Created {orders_count} orders with items"))

        # Generate Reviews
        self.stdout.write("📝 Generating reviews...")
        reviews_created = 0
        for product in products:
            try:
                # Each product gets 0-5 reviews
                num_reviews = random.randint(0, 5)
                for _ in range(num_reviews):
                    user = random.choice(users)
                    # Avoid duplicate reviews
                    if not Review.objects.filter(product=product, user=user).exists():
                        Review.objects.create(
                            product=product,
                            user=user,
                            content=fake.paragraph(nb_sentences=3)
                        )
                        reviews_created += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Error creating review: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"✓ Created {reviews_created} reviews"))

        # Generate Wishlists
        self.stdout.write("📝 Generating wishlists...")
        for user in users:
            try:
                wishlist, created = Wishlist.objects.get_or_create(user=user)
                # Add 0-5 products to each wishlist
                num_products = random.randint(0, 5)
                wishlist_products = random.sample(products, min(num_products, len(products)))
                wishlist.products.set(wishlist_products)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Error creating wishlist: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"✓ Created wishlists for all users"))

        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("✅ Fake data generation completed!"))
        self.stdout.write("="*50)
        self.stdout.write(f"👥 Users: {len(users)}")
        self.stdout.write(f"🏪 Sellers: {len(sellers)}")
        self.stdout.write(f"📁 Categories: {len(categories)}")
        self.stdout.write(f"📦 Products: {len(products)}")
        self.stdout.write(f"🛒 Orders: {orders_count}")
        self.stdout.write(f"⭐ Reviews: {reviews_created}")
        self.stdout.write(f"❤️  Wishlists: {len(users)}\n")
