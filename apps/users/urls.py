from django.urls import path, include
from .views import InitialRegistrationView, VerifyCodeView, RegisterUserView, CustomTokenObtainPairView, PasswordResetRequestView, PasswordResetConfirmView, GoogleLogin
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('register/initial/', InitialRegistrationView.as_view(), name='register_initial'),
    path('register/verify/', VerifyCodeView.as_view(), name='register_verify'),
    path('register/complete/', RegisterUserView.as_view(), name='register_complete'),
    
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('social/google/login/', GoogleLogin.as_view(), name='google_login'),
]