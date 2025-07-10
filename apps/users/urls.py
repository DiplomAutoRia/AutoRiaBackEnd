from django.urls import path
from .views import InitialRegistrationView, VerifyCodeView, RegisterUserView

urlpatterns = [
    path('register/initial/', InitialRegistrationView.as_view(), name='register_initial'),
    path('register/verify/', VerifyCodeView.as_view(), name='register_verify'),
    path('register/complete/', RegisterUserView.as_view(), name='register_complete'),
]