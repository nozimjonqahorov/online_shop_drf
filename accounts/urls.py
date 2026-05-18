from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignUpView

urlpatterns = [
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', SignUpView.as_view(), name='signup'),
]
