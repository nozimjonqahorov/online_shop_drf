from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    SignUpView,
    VerifyCodeView,
    ResendCodeView,
    ChangeProfileInfoView,
    UploadProfilePhotoView,
    ProfileView,
    ProfileUpdateView,
    LoginView,
    LogoutView,
)

urlpatterns = [
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("verify-code/", VerifyCodeView.as_view(), name="verify-code"),
    path("resend-code/", ResendCodeView.as_view(), name="resend-code"),
    path("change-profile-info/", ChangeProfileInfoView.as_view(), name="change-profile-info"),
    path("upload-photo/", UploadProfilePhotoView.as_view(), name="upload-photo"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile-update"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

