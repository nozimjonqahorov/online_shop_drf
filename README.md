# Marketplace API

This repository contains a Django REST API for a small online marketplace. The project currently provides user authentication, product catalog, cart, wishlist, and order management.

## What is included

- JWT-based authentication and profile management
- Product and category APIs
- Shopping cart and wishlist support
- Order creation, payment flow, and seller order views
- Swagger / ReDoc documentation
- Sample data generation command for development

## Main modules

- accounts: registration, login, logout, profile, password reset, email/phone verification
- products: categories, products, cart, reviews
- orders: order lifecycle, payment handling, seller dashboards, wishlist
- shared: common helpers and utilities
- config: Django settings and URL routing

## Tech stack

- Python 3.12+
- Django 6.0.5
- Django REST Framework 3.17.1
- djangorestframework-simplejwt 5.5.1
- drf-yasg 1.21.15
- Pillow 12.2.0
- Faker 40.21.0

## Quick start

1. Create and activate a virtual environment
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies
   ```powershell
   pip install -r requirements.txt
   ```

3. Apply database migrations
   ```powershell
   python manage.py migrate
   ```

4. Run the development server
   ```powershell
   python manage.py runserver
   ```

5. Open API docs
   - Swagger: http://127.0.0.1:8000/swagger/
   - ReDoc: http://127.0.0.1:8000/redoc/

## Useful development commands

Generate sample data:
```powershell
python manage.py generate_fake_data --users 10 --sellers 3 --categories 5 --products 20 --orders 10
```

Run checks:
```powershell
python manage.py check
```

## API overview

- /auth/… — signup, login, logout, profile, password reset, verification
- /products/… — categories, products, cart operations, review creation
- /orders/… — orders, seller order views, wishlist, payment endpoint

## Notes

- The project uses SQLite by default in this repository.
- The old requirements file contained many environment-specific packages; it has been cleaned to match the actual project dependencies used here.

## License

This project is intended for educational and development use.
