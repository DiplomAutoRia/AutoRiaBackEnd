from rest_framework import serializers
from .models import Favorite
from apps.vehicles.serializers import VehicleDetailSerializer 

class FavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['vehicle']
        read_only_fields = ['user']

    def create(self, validated_data):
        user = validated_data.pop('user')
        vehicle = validated_data['vehicle']
        
        if Favorite.objects.filter(user=user, vehicle=vehicle).exists():
            raise serializers.ValidationError({"detail": "This vehicle is already in your favorites."})
            
        return Favorite.objects.create(user=user, **validated_data)

class FavoriteSerializer(serializers.ModelSerializer):
    vehicle_details = VehicleDetailSerializer(source='vehicle', read_only=True)
    created_at = serializers.DateTimeField(source='added_at', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'vehicle', 'vehicle_details', 'created_at']