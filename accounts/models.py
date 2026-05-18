from django.db import models
from shared.models import BaseModel
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta
from django.utils import timezone
from config.settings import EMAIL_EXPIRATION_TIME, PHONE_EXPIRATION_TIME
import uuid 
import random
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken


# Create your models here.

ORDINARY_USER, SELLER, ADMIN = ("ordinary_user", "seller", "admin")
VIA_PHONE,  VIA_EMAIL = ("via_phone", "via_email")
NEW, CODE_VERIFY, CHANGE_INFO, DONE = ("new", "code_verify", "change_info", "done")

class CustomUser(AbstractUser, BaseModel):
    USER_ROLE = (
       (ORDINARY_USER, ORDINARY_USER),
       (SELLER, SELLER),
       (ADMIN, ADMIN)
    )

    AUTH_TYPE = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL),
    )

    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFY, CODE_VERIFY),
        (CHANGE_INFO, CHANGE_INFO),
        (DONE, DONE),
    )

    user_role = models.CharField(max_length=250, choices = USER_ROLE, default = ORDINARY_USER)
    auth_type = models.CharField(max_length=250, choices = AUTH_TYPE)
    auth_status = models.CharField(max_length=250, choices = AUTH_STATUS, default = NEW)
    email = models.EmailField(unique=True, null=True)
    phone_number = models.CharField(max_length=13, unique=True, null=True)
    photo = models.ImageField(upload_to="users/", null=True, default="users/default_user.png")

    def __str__(self):
        return f"{self.username} | {self.user_role}"
    
    def check_username(self):
        if not self.username:
            temp_username = f"user_{str(uuid.uuid4()).split('-')[-1]}"
            while CustomUser.objects.filter(username=temp_username).exists():
                temp_username += str(random.randint(0, 100))
            self.username = temp_username

    def generate_and_hash_password(self):
        if not self.password:
            self.password = str(uuid.uuid4()).split('-')[-1]
        
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)

    def email_normalize(self):
        if self.email:
            self.email = self.email.lower().strip()
    
    def clean(self):
        self.check_username()
        self.email_normalize()
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()  # clean() metodini avtomatik ishga tushiradi
        self.generate_and_hash_password() 
        super().save(*args, **kwargs)

    def token(self):
        refresh = RefreshToken.for_user(self)

        return {
            "access_token": str(refresh.access_token),
            "refresh": str(refresh)
        }

    def create_code(self, verify_type):
        code = str(random.randint(1000, 9999))
        CodeVerify.objects.create(
            code=code,
            user=self,
            verify_type=verify_type
        )
        return code


class CodeVerify(BaseModel):

    VERIFY_TYPE = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL),
    )

    code = models.CharField(max_length=4)
    verify_type =models.CharField(max_length=120, choices=VERIFY_TYPE)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="verify_codes", null=True)
    is_used = models.BooleanField(default=False)
    expiration_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.pk:
            current_time = timezone.now()
            if self.verify_type == VIA_EMAIL:
                self.expiration_time = current_time + timedelta(minutes=EMAIL_EXPIRATION_TIME)
            else:
                self.expiration_time = current_time + timedelta(minutes=PHONE_EXPIRATION_TIME)
        super().save(*args, **kwargs)

