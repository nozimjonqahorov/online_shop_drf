from django.shortcuts import render
from .models import VIA_EMAIL, VIA_PHONE, SELLER, ORDINARY_USER
from rest_framework.generics import CreateAPIView
from rest_framework import permissions
from .serializers import SignUpSerializer
from .models import CustomUser
# Create your views here.


class SignUpView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer
    queryset = CustomUser.objects.all()