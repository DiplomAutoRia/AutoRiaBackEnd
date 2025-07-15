from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from django.core.cache import cache
from .serializers import (
    InitialRegistrationSerializer,
    VerificationSerializer,
    SetPasswordSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer 
)
from .utils import (
    generate_verification_code,
    send_verification_email,
    send_verification_sms,
    store_verification_code,
    get_verification_code,
    delete_verification_code
)

from django.conf import settings

from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

class InitialRegistrationView(APIView):
    def post(self, request):
        serializer = InitialRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            contact_info_data = serializer.validated_data['contact_info']
            contact_type = contact_info_data['type']
            contact_value = contact_info_data['value']

            code = generate_verification_code()
            store_verification_code(contact_value, code)

            if contact_type == 'email':
                send_verification_email(contact_value, code)
            else:
                send_verification_sms(contact_value, code)

            cache.set(f'registration_data_{contact_value}',
                      {'first_name': first_name, 'last_name': last_name, 'contact_type': contact_type},
                      timeout=300)

            return Response(
                {"detail": f"Verification code sent to your {contact_type}."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid():
            contact_info = serializer.validated_data['contact_info']
            code_entered = serializer.validated_data['code']

            stored_code = get_verification_code(contact_info)

            if not stored_code or stored_code != code_entered:
                return Response(
                    {"detail": "Invalid or expired verification code."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cache.set(f'is_verified_{contact_info}', True, timeout=300)
            delete_verification_code(contact_info)

            return Response(
                {"detail": "Verification successful. Now you can set your password."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterUserView(APIView):
    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            contact_info = serializer.validated_data['contact_info']
            password = serializer.validated_data['password']

            is_verified = cache.get(f'is_verified_{contact_info}')
            if not is_verified:
                return Response(
                    {"detail": "Contact information is not verified. Please complete verification first."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            registration_data = cache.get(f'registration_data_{contact_info}')
            if not registration_data:
                return Response(
                    {"detail": "Registration data not found or expired. Please restart the registration process."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            first_name = registration_data['first_name']
            last_name = registration_data['last_name']
            contact_type = registration_data['contact_type']

            username = f"{first_name} {last_name}".strip()
            if not username:
                username = contact_info

            user_data = {
                'first_name': first_name,
                'last_name': last_name,
                'is_verified': True,
                'username': username,
            }

            if contact_type == 'email':
                user_data['email'] = contact_info
            else:
                user_data['phone_number'] = contact_info

            try:
                user = User.objects.create_user(password=password, **user_data)

                delete_verification_code(contact_info)
                cache.delete(f'is_verified_{contact_info}')
                cache.delete(f'registration_data_{contact_info}')

                return Response(
                    {"detail": "User registered successfully."},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"detail": f"Error creating user: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = LoginSerializer

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            contact_info_data = serializer.validated_data['contact_info']
            contact_type = contact_info_data['type']
            contact_value = contact_info_data['value']

            user = User.objects.filter(
                Q(email__iexact=contact_value) | Q(phone_number=contact_value)
            ).first()

            if not user:
                return Response(
                    {"detail": "If an account exists, a reset code will be sent."},
                    status=status.HTTP_200_OK
                )

            code = generate_verification_code()
            store_verification_code(contact_value, code)

            if contact_type == 'email':
                send_verification_email(contact_value, code)
            else:
                send_verification_sms(contact_value, code)

            cache.set(f'password_reset_initiated_{contact_value}', True, timeout=300)

            return Response(
                {"detail": f"Verification code sent to your {contact_type} for password reset."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            contact_info = serializer.validated_data['contact_info']
            code_entered = serializer.validated_data['code']
            new_password = serializer.validated_data['password']

            is_reset_initiated = cache.get(f'password_reset_initiated_{contact_info}')
            if not is_reset_initiated:
                return Response(
                    {"detail": "Password reset process not initiated or expired for this contact information. Please make a new request."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            stored_code = get_verification_code(contact_info)

            if not stored_code or stored_code != code_entered:
                return Response(
                    {"detail": "Invalid or expired verification code."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.filter(
                Q(email__iexact=contact_info) | Q(phone_number=contact_info)
            ).first()

            if not user:
                return Response(
                    {"detail": "User not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            user.set_password(new_password)
            user.save()

            delete_verification_code(contact_info)
            cache.delete(f'password_reset_initiated_{contact_info}')

            return Response(
                {"detail": "Password changed successfully. You can now log in with your new password."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)