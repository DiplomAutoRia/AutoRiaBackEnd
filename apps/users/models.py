from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = [
    ('user', 'User'),
    ('admin', 'Admin'),
    ('moderator', 'Moderator'),
]

class User(AbstractUser):
    
    email = models.EmailField(unique=True, verbose_name='Email')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone number')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='Location')
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Role',
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    is_verified = models.BooleanField(default=False, verbose_name='Verified')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
