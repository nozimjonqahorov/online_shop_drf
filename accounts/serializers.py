from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import CustomUser, CodeVerify, VIA_EMAIL, VIA_PHONE
from shared.utility import check_email_or_phone

class SignUpSerializer(serializers.ModelSerializer):
    # Modelda bo'lmagan, lekin foydalanuvchidan qabul qilinadigan vaqtinchalik maydon
    email_or_phone = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'auth_type', 'auth_status', 'email_or_phone']
        read_only_fields = ['auth_type', 'auth_status']

    def validate_email_or_phone(self, value):
        value = value.strip().lower()
        
        field_type = check_email_or_phone(value)
        
        if field_type == 'email':
            if CustomUser.objects.filter(email=value).exists():
                raise ValidationError({"email_or_phone": "Bu email manzili allaqachon ro'yxatdan o'tgan!"})
        elif field_type == 'phone':
            if CustomUser.objects.filter(phone_number=value).exists():
                raise ValidationError({"email_or_phone": "Bu telefon raqami allaqachon ro'yxatdan o'tgan!"})
                
        return value

    def create(self, validated_data):
        email_or_phone = validated_data.pop('email_or_phone')
        field_type = check_email_or_phone(email_or_phone)
        

        if field_type == 'email':
            validated_data['email'] = email_or_phone
            validated_data['auth_type'] = VIA_EMAIL
        else:
            validated_data['phone_number'] = email_or_phone
            validated_data['auth_type'] = VIA_PHONE
            
        user = CustomUser.objects.create(**validated_data)
        return user

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)

        if user.auth_type == VIA_EMAIL:
            code = user.create_code(VIA_EMAIL)
            # send_mail(user.email, code)
            print(f"Email kod: {code}")
            
        elif user.auth_type == VIA_PHONE:
            code = user.create_code(VIA_PHONE)
            # send_phone(user.phone_number, code)
            print(f"Telefon kod: {code}")

        return user
    
    @staticmethod
    def auth_validate(data):
        user_input = data.get('email_or_phone')
        user_input_type = check_email_or_phone(user_input)
        if user_input_type == 'email':
            data = {
                'email': user_input,
                'auth_type': VIA_EMAIL
            }
        elif user_input_type == 'phone':
            data = {
                'phone_number': user_input,
                'auth_type': VIA_PHONE
            }
        else:
            raise ValidationError({
                'message': 'Email yoki phone number xato kiritildi!'
            })
        return data
    
    def validate(self, attrs):
        attrs = self.auth_validate(attrs)
        return attrs
    

    def to_representation(self, instance):
        user = super().to_representation(instance)
        user['token'] = instance.token()
        return user