from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import CustomUser, VIA_EMAIL, VIA_PHONE
from shared.utility import check_email_or_phone
from shared.utils import send_to_mail




class SignUpSerializer(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'auth_type', 'auth_status', 'email_or_phone']
        read_only_fields = ['auth_type', 'auth_status']

    def validate(self, attrs):
        user_input = attrs.get('email_or_phone', '')
        
        # Funksiyadan turning o'zi va formatlangan qiymat qaytadi
        field_type, cleaned_value = check_email_or_phone(user_input)

        if field_type == 'email':
            if CustomUser.objects.filter(email=cleaned_value).exists():
                raise ValidationError({"email_or_phone": "Bu email manzili allaqachon ro'yxatdan o'tgan!"})
        
            attrs['email'] = cleaned_value
            attrs['auth_type'] = VIA_EMAIL

        elif field_type == 'phone':
            if CustomUser.objects.filter(phone_number=cleaned_value).exists():
                raise ValidationError({"email_or_phone": "Bu telefon raqami allaqachon ro'yxatdan o'tgan!"})

            attrs['phone_number'] = cleaned_value
            attrs['auth_type'] = VIA_PHONE

        attrs.pop('email_or_phone', None)
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)

        if user.auth_type == VIA_EMAIL:
            code = user.create_code(VIA_EMAIL)
            send_to_mail(user.email, code)
            print(f"Email kod: {code}")
            
        elif user.auth_type == VIA_PHONE:
            code = user.create_code(VIA_PHONE)
            # send_phone(user.phone_number, code)
            print(f"Telefon kod: {code}")

        return user
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['token'] = instance.token()
        return data