from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = [
    ('user', 'User'),
    ('admin', 'Admin'),
    ('moderator', 'Moderator'),
]

class User(AbstractUser):
    
    email = models.EmailField(unique=True, verbose_name='Email', help_text="User's unique email address")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone number', help_text="User's phone number")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='Location', help_text="User's location")
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Role',
        help_text='Role of the user in the system'
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar', help_text="User's avatar image")
    is_verified = models.BooleanField(default=False, verbose_name='Verified', help_text="Email/phone is verified")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
