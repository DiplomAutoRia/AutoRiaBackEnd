from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Favorite
from .serializers import FavoriteSerializer, FavoriteCreateSerializer
from django.contrib.auth.models import AnonymousUser

class FavoriteListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if isinstance(self.request.user, AnonymousUser):
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FavoriteCreateSerializer
        return FavoriteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriteDestroyView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    queryset = Favorite.objects.all()

    def get_queryset(self):
        if isinstance(self.request.user, AnonymousUser):
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except NotFound:
            return Response(
                {"detail": "Favorite not found or you do not have permission to delete it."},
                status=status.HTTP_404_NOT_FOUND
            )