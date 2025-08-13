from rest_framework import viewsets, permissions, serializers
from .models import Report
from .serializers import ReportSerializer, ReportCreateSerializer
from apps.vehicles.models import Vehicle

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class ReportViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReportCreateSerializer
        return ReportSerializer

    def get_queryset(self):
        vehicle_id = self.kwargs.get('vehicle_pk')
        if vehicle_id:
            return Report.objects.filter(vehicle=vehicle_id).order_by('-created_at')

        return Report.objects.none()

    def perform_create(self, serializer):
        vehicle_id = self.kwargs.get('vehicle_pk')
        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError({"detail": "Vehicle not found."})

        if Report.objects.filter(user=self.request.user, vehicle=vehicle).exists():
            raise serializers.ValidationError({"detail": "You have already submitted a report for this vehicle."})

        serializer.save(user=self.request.user, vehicle=vehicle)