from rest_framework import viewsets, permissions, serializers
from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer
from apps.vehicles.models import Vehicle

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        vehicle_id = self.kwargs.get('vehicle_pk')
        if not vehicle_id:
            return Comment.objects.none()

        return Comment.objects.filter(vehicle=vehicle_id).order_by('-created_at')

    def perform_create(self, serializer):
        vehicle_id = self.kwargs.get('vehicle_pk')
        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError({"detail": "Vehicle not found."})

        serializer.save(user=self.request.user, vehicle=vehicle)