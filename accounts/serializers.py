from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from .models import (
    CustomUser,
    VIA_EMAIL,
    VIA_PHONE,
    CODE_VERIFY,
    CodeVerify,
    CHANGE_INFO,
    UPLOAD_AVATAR_DONE,
)
from shared.utility import check_email_or_phone
from shared.utils import send_to_mail


class SignUpSerializer(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ["id", "auth_type", "auth_status", "email_or_phone"]
        read_only_fields = ["auth_type", "auth_status"]

    def validate(self, attrs):
        user_input = attrs.get("email_or_phone", "")
        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            if CustomUser.objects.filter(email=cleaned_value).exists():
                raise ValidationError({"email_or_phone": "Bu email manzili allaqachon ro'yxatdan o'tgan!"})
            attrs["email"] = cleaned_value
            attrs["auth_type"] = VIA_EMAIL

        elif field_type == "phone":
            if CustomUser.objects.filter(phone_number=cleaned_value).exists():
                raise ValidationError({"email_or_phone": "Bu telefon raqami allaqachon ro'yxatdan o'tgan!"})
            attrs["phone_number"] = cleaned_value
            attrs["auth_type"] = VIA_PHONE

        attrs.pop("email_or_phone", None)
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)

        if user.auth_type == VIA_EMAIL:
            code = user.create_code(VIA_EMAIL)
            send_to_mail(user.email, code)
            print(f"Email kod: {code}")
        elif user.auth_type == VIA_PHONE:
            code = user.create_code(VIA_PHONE)
            print(f"Telefon kod: {code}")

        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["token"] = instance.token()
        return data


class VerifyCodeSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True, write_only=True)
    code = serializers.CharField(max_length=4, required=True, write_only=True)

    def validate(self, attrs):
        user_input = attrs.get("email_or_phone", "")
        code = attrs.get("code", "").strip()
        print(user_input)
        print(code)
        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            user = CustomUser.objects.filter(email=cleaned_value).first()
            print(user)
        else:
            user = CustomUser.objects.filter(phone_number=cleaned_value).first()

        if not user:
            raise ValidationError({"message": "Foydalanuvchi topilmadi!"})

        verify_code = CodeVerify.objects.filter(user=user, code=code, is_used=False).order_by("-created_at").first()
        print(verify_code)

        if not verify_code:
            raise ValidationError({"code": "Tasdiqlash kodi xato!"})

        if verify_code.expiration_time and verify_code.expiration_time < timezone.now():
            raise ValidationError({"code": "Kodning amal qilish vaqti tugagan!"})

        attrs["user"] = user
        attrs["verify_code"] = verify_code
        return attrs


class ResendCodeSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user_input = attrs.get("email_or_phone", "")
        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            user = CustomUser.objects.filter(email=cleaned_value).first()
        else:
            user = CustomUser.objects.filter(phone_number=cleaned_value).first()

        if not user:
            raise ValidationError({"message": "Foydalanuvchi topilmadi!"})

        active_code = CodeVerify.objects.filter(
            user=user,
            is_used=False,
            expiration_time__gte=timezone.now(),
        ).order_by("-created_at").first()

        if active_code:
            raise ValidationError({"message": f"Sizda hali aktiv kod mavjud {active_code.expiration_time}"})

        attrs["user"] = user
        return attrs


class ChangeProfileInfoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=True, max_length=100)
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    user_role = serializers.CharField(required=True, max_length=100)

    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "password", "confirm_password", "user_role"]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise ValidationError({"password": "Parollar bir-biriga mos kelmadi!"})
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("confirm_password", None)
        password = validated_data.pop("password", None)
        
        instance.username =  validated_data.get("username", instance.username)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.user_role = validated_data.get("user_role", instance.user_role)

        if password:
            instance.set_password(password)

        instance.auth_status = CHANGE_INFO
        instance.save()
        return instance


class UploadProfilePhotoSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=True)

    class Meta:
        model = CustomUser
        fields = ["photo"]

    def update(self, instance, validated_data):
        instance.photo = validated_data.get("photo", instance.photo)
        instance.auth_status = UPLOAD_AVATAR_DONE
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "photo",
            "user_role"
        ]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "user_role", "photo"]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "user_role": {"required": False},
        }

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.user_role = validated_data.get("user_role", instance.user_role)

        if "photo" in validated_data:
            instance.photo = validated_data.get("photo")

        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user_input = attrs.get("email_or_phone", "")
        password = attrs.get("password", "")
        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            user = CustomUser.objects.filter(email=cleaned_value).first()
        else:
            user = CustomUser.objects.filter(phone_number=cleaned_value).first()

        if not user or not user.check_password(password):
            raise ValidationError({"message": "Email/telefon yoki parol noto'g'ri"})

        attrs["user"] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user_input = attrs.get("email_or_phone", "")
        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            user = CustomUser.objects.filter(email=cleaned_value).first()
            verify_type = VIA_EMAIL
        else:
            user = CustomUser.objects.filter(phone_number=cleaned_value).first()
            verify_type = VIA_PHONE

        if not user:
            raise ValidationError({"message": "Foydalanuvchi topilmadi!"})

        attrs["user"] = user
        attrs["verify_type"] = verify_type
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True, write_only=True)
    code = serializers.CharField(max_length=4, required=True, write_only=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise ValidationError({"confirm_password": "Parollar bir-biriga mos kelmadi!"})

        user_input = attrs.get("email_or_phone", "")
        code = attrs.get("code", "").strip()

        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == "email":
            user = CustomUser.objects.filter(email=cleaned_value).first()
            verify_type = VIA_EMAIL
        else:
            user = CustomUser.objects.filter(phone_number=cleaned_value).first()
            verify_type = VIA_PHONE

        if not user:
            raise ValidationError({"message": "Foydalanuvchi topilmadi!"})

        verify_code = CodeVerify.objects.filter(
            user=user,
            verify_type=verify_type,
            code=code,
            is_used=False,
        ).order_by("-created_at").first()

        if not verify_code:
            raise ValidationError({"code": "Tasdiqlash kodi xato!"})

        from django.utils import timezone

        if verify_code.expiration_time and verify_code.expiration_time < timezone.now():
            raise ValidationError({"code": "Kodning amal qilish vaqti tugagan!"})

        attrs["user"] = user
        attrs["verify_code"] = verify_code
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user:
            raise ValidationError({"message": "Authentication required"})

        if attrs["new_password"] != attrs["confirm_password"]:
            raise ValidationError({"confirm_password": "Parollar bir-biriga mos kelmadi!"})

        if not user.check_password(attrs["old_password"]):
            raise ValidationError({"old_password": "Eski parol noto'g'ri"})

        attrs["user"] = user
        return attrs


