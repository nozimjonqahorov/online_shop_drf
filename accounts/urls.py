from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignUpView, VerifyCodeView, ResendCodeView, ChangeProfileInfoView, UploadProfilePhotoView

urlpatterns = [
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('resend-code/', ResendCodeView.as_view(), name='resend-code'),
    path('change-profile-info/', ChangeProfileInfoView.as_view(), name='change-profile-info'),
    path('upload-photo/', UploadProfilePhotoView.as_view(), name='upload-photo'),
]
