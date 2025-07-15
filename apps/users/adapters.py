from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        if hasattr(user, 'email') and user.email:
            user.username = user.email
        else:
            from allauth.socialaccount.models import SocialAccount
            social_account = SocialAccount.objects.filter(user=user).first()
            if social_account:
                user.username = social_account.uid 
            else:
                user.username = get_user_model().objects.make_random_password(length=30) 


        social_data = None
        if hasattr(user, 'socialaccount_set'):
            social_account = user.socialaccount_set.first()
            if social_account and social_account.extra_data:
                social_data = social_account.extra_data

        if social_data:
            user.first_name = social_data.get('given_name', social_data.get('first_name', ''))
            user.last_name = social_data.get('family_name', social_data.get('last_name', ''))

        user.is_verified = True 

        return super().save_user(request, user, form, commit)
