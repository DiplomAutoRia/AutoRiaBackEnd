from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter # ДОДАЙТЕ ЦЕЙ ІМПОРТ

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        if hasattr(user, 'email') and user.email:
            user.username = user.email
        elif not user.username:
            from allauth.socialaccount.models import SocialAccount
            social_account = SocialAccount.objects.filter(user=user).first()
            if social_account:
                user.username = social_account.uid 
            else:
                user.username = get_user_model().objects.make_random_password(length=30) 
        
        social_account_data = None
        if hasattr(user, 'socialaccount_set') and user.socialaccount_set.exists():
            social_account_data = user.socialaccount_set.first().extra_data

        if social_account_data:
            user.first_name = social_account_data.get('given_name', social_account_data.get('first_name', ''))
            user.last_name = social_account_data.get('family_name', social_account_data.get('last_name', ''))
            user.is_verified = True

        return super().save_user(request, user, form, commit)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        pass
        
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        return user