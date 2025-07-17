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
    PasswordResetConfirmSerializer,
    GoogleLoginSerializer,
    UserProfileUpdateSerializer,
    ContactInfoVerificationSerializer
)

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.permissions import IsAuthenticated

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
    
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = settings.SOCIAL_LOGIN_CALLBACK_URL
    serializer_class = GoogleLoginSerializer
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileUpdateSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()

            response_data = {"detail": "User profile updated successfully."}

            if updated_user.email is None and cache.get(f'unverified_email_{request.user.id}'):
                code = generate_verification_code()
                unverified_email = cache.get(f'unverified_email_{request.user.id}')
                store_verification_code(unverified_email, code)
                send_verification_email(unverified_email, code)
                response_data["detail"] += " Verification code sent to your new email. Please verify it."
                response_data["email_verification_required"] = True
            
            if updated_user.phone_number is None and cache.get(f'unverified_phone_{request.user.id}'):
                code = generate_verification_code()
                unverified_phone = cache.get(f'unverified_phone_{request.user.id}')
                store_verification_code(unverified_phone, code)
                send_verification_sms(unverified_phone, code)
                response_data["detail"] += " Verification code sent to your new phone number. Please verify it."
                response_data["phone_verification_required"] = True
            
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactInfoVerificationUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContactInfoVerificationSerializer(data=request.data)
        if serializer.is_valid():
            contact_info = serializer.validated_data['contact_info']
            code_entered = serializer.validated_data['code']

            stored_code = get_verification_code(contact_info)

            if not stored_code or stored_code != code_entered:
                return Response(
                    {"detail": "Invalid or expired verification code."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = request.user
            detail_message = ""

            unverified_email = cache.get(f'unverified_email_{user.id}')
            unverified_phone = cache.get(f'unverified_phone_{user.id}')

            if unverified_email == contact_info:
                user.email = unverified_email
                user.is_verified = True
                cache.delete(f'unverified_email_{user.id}')
                delete_verification_code(contact_info)
                detail_message = "Email successfully verified and updated."
            elif unverified_phone == contact_info:
                user.phone_number = unverified_phone
                user.is_verified = True
                cache.delete(f'unverified_phone_{user.id}')
                delete_verification_code(contact_info)
                detail_message = "Phone number successfully verified and updated."
            else:
                return Response(
                    {"detail": "Provided contact information does not match any pending verification requests for this user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.save()
            return Response({"detail": detail_message}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return Response({"detail": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)