from django.urls import path
from .views import FavoriteListCreateView, FavoriteDestroyView

urlpatterns = [
    path('', FavoriteListCreateView.as_view(), name='favorite-list-create'),

    path('<int:pk>/', FavoriteDestroyView.as_view(), name='favorite-destroy'),
]