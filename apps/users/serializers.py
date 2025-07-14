from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
import re

User = get_user_model()

class InitialRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        max_length=150,
        required=True,
        error_messages={
            'required': 'First name is required.',
            'max_length': 'First name cannot exceed 150 characters.'
        }
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
        error_messages={
            'required': 'Last name is required.',
            'max_length': 'Last name cannot exceed 150 characters.'
        }
    )
    contact_info = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Contact information (email or phone number) is required.'
        }
    )

    def validate_contact_info(self, value):
        cleaned_value = re.sub(r'[()\s-]', '', value)

        is_email = False
        is_phone = False

        try:
            validate_email(cleaned_value)
            is_email = True
        except ValidationError:
            pass

        phone_regex = r"^(?:\+|0)[0-9]{7,20}$"

        if re.fullmatch(phone_regex, cleaned_value):
            is_phone = True

        if not is_email and not is_phone:
            raise serializers.ValidationError("Please enter a valid email address or phone number.")

        user_exists = User.objects.filter(
            Q(email__iexact=cleaned_value) | Q(phone_number=cleaned_value)
        ).exists()

        if user_exists:
            raise serializers.ValidationError("User with this email or phone number already exists.")
        
        if is_phone and not cleaned_value.startswith('+'):
            if re.fullmatch(r'^0[0-9]{9}$', cleaned_value):
                cleaned_value = '+38' + cleaned_value[1:]
            
        if is_email:
            return {'type': 'email', 'value': cleaned_value}
        else: 
            return {'type': 'phone', 'value': cleaned_value}

class VerificationSerializer(serializers.Serializer):
    contact_info = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Contact information is required for verification.'
        }
    )
    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        error_messages={
            'required': 'Verification code is required.',
            'min_length': 'Verification code must be 6 digits.',
            'max_length': 'Verification code must be 6 digits.'
        }
    )

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Verification code must contain only digits.")
        return value

class SetPasswordSerializer(serializers.Serializer):
    contact_info = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Contact information is required to set the password.'
        }
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        error_messages={
            'required': 'Password is required.',
            'min_length': 'Password must be at least 6 characters long.'
        }
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        error_messages={
            'required': 'Password confirmation is required.',
            'min_length': 'Password confirmation must be at least 6 characters long.'
        }
    )

    def validate_password(self, value):
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter.")

        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data