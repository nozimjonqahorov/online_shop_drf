from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import (
    VIA_EMAIL,
    VIA_PHONE,
    NEW, 
    CODE_VERIFY,
    CHANGE_INFO,
    UPLOAD_AVATAR_DONE,
    DONE
)
from .models import CustomUser
from .serializers import (
    SignUpSerializer,
    VerifyCodeSerializer,
    ResendCodeSerializer,
    ChangeProfileInfoSerializer,
    UploadProfilePhotoSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
)


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from shared.utils import send_to_mail


class SignUpView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer
    queryset = CustomUser.objects.all()


class VerifyCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = VerifyCodeSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            verify_code = serializer.validated_data["verify_code"]

            verify_code.is_used = True
            verify_code.save()

            user.auth_status = CODE_VERIFY
            user.save()

            return Response(
                {
                    "success": True,
                    "message": "Akkount muvaffaqiyatli tasdiqlandi.",
                    "auth_status": user.auth_status,
                    "tokens": user.token(),
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendCodeView(APIView):
    
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = ResendCodeSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            code = user.create_code(user.auth_type)

            if user.auth_type == VIA_EMAIL:
                send_to_mail(
                    message=f"Sizning yangi tasdiqlash kodingiz: {code}",
                    email=user.email,
                )
            elif user.auth_type == VIA_PHONE:
                print(f"Yangi Telefon kod: {code}")

            return Response(
                {
                    "success": True,
                    "message": "Yangi tasdiqlash kodi yuborildi.",
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ChangeProfileInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user

        if user.auth_status in [UPLOAD_AVATAR_DONE, DONE]:
            return Response(
                {"message": "Siz bu qismdan o'tib bo'lgansiz"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.auth_status == NEW:
            return Response(
                {"message": "Siz avval kodni tasdiqlashingiz kerak!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ChangeProfileInfoSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user.auth_status = CHANGE_INFO
            return Response(
                {
                    "success": True,
                    "message": "Ism va parollar muvaffaqiyatli saqlandi. Endi rasm yuklang.",
                    "auth_status": user.auth_status,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadProfilePhotoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, *args, **kwargs):
        user = request.user

        if user.auth_status != CHANGE_INFO:
            return Response(
                {"message": "Siz avval ism sharif va parollarni kiritishingiz kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UploadProfilePhotoSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!",
                    "auth_status": user.auth_status,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = ProfileSerializer(request.user)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def put(self, request, *args, **kwargs):
        serializer = ProfileUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            return Response(
                {"success": True, "message": "Login muvaffaqiyatli", "tokens": user.token()},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"message": "refresh token taqdim etilishi shart"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"success": True, "message": "Logout muvaffaqiyatli"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"message": "Xato refresh token"}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        verify_type = serializer.validated_data["verify_type"]

        code = user.create_code(verify_type)

        if verify_type == VIA_EMAIL:
            send_to_mail(
                message=f"Sizning parolni tiklash (reset) kodingiz: {code}",
                email=user.email,
            )
        else:
            print(f"Yangi kod ): {code}")

        return Response(
            {
                "success": True,
                "message": "Reset uchun kod yuborildi.",
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        verify_code = serializer.validated_data["verify_code"]
        new_password = serializer.validated_data["new_password"]

        verify_code.is_used = True
        verify_code.save()

        user.set_password(new_password)
        user.save()

        return Response(
            {
                "success": True,
                "message": "Parol muvaffaqiyatli yangilandi.",
                "tokens": user.token(),
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        new_password = serializer.validated_data["new_password"]

        user.set_password(new_password)
        user.save()

        return Response(
            {
                "success": True,
                "message": "Parol muvaffaqiyatli o'zgartirildi.",
            },
            status=status.HTTP_200_OK,
        )


