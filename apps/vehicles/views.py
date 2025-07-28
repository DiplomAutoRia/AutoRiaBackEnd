from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny

from .models import (
    Vehicle, VehicleImage, Car, Motorcycle, Truck, Trailer,
    SpecialTech, Bus, WaterTransport, AirTransport, Motorhome
)
from .serializers import (
    VehicleSerializer, VehicleImageSerializer,
    CarSerializer, MotorcycleSerializer, TruckSerializer,
    TrailerSerializer, SpecialTechSerializer, BusSerializer, WaterTransportSerializer,
    AirTransportSerializer, MotorhomeSerializer
)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class IsOwnerOrReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().select_related(
        'car', 'motorcycle', 'truck', 'trailer', 'specialtech',
        'bus', 'watertransport', 'airtransport', 'motorhome'
    )
    permission_classes = [IsOwnerOrReadOnly] 

    VEHICLE_TYPES = {
        'car': {'model': Car, 'serializer': CarSerializer},
        'motorcycle': {'model': Motorcycle, 'serializer': MotorcycleSerializer},
        'truck': {'model': Truck, 'serializer': TruckSerializer},
        'trailer': {'model': Trailer, 'serializer': TrailerSerializer},
        'specialtech': {'model': SpecialTech, 'serializer': SpecialTechSerializer},
        'bus': {'model': Bus, 'serializer': BusSerializer},
        'watertransport': {'model': WaterTransport, 'serializer': WaterTransportSerializer},
        'airtransport': {'model': AirTransport, 'serializer': AirTransportSerializer},
        'motorhome': {'model': Motorhome, 'serializer': MotorhomeSerializer},
    }

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        return VehicleSerializer

    def get_object(self):
        obj = super().get_object()
        if self.request.method == 'GET':
            obj.views_count += 1
            obj.save(update_fields=['views_count'])
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['view'] = self
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    _common_vehicle_properties = {
        'brand': openapi.Schema(type=openapi.TYPE_STRING, description='Vehicle brand'),
        'model': openapi.Schema(type=openapi.TYPE_STRING, description='Vehicle model'),
        'year': openapi.Schema(type=openapi.TYPE_INTEGER, format=openapi.FORMAT_INT64, description='Production year (1900–next year)'),
        'price': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description='Price of the vehicle'),
        'currency': openapi.Schema(type=openapi.TYPE_STRING, description='Currency (e.g., USD, EUR)'),
        'description': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed description of the vehicle'),
        'location': openapi.Schema(type=openapi.TYPE_STRING, description='Location of the vehicle (optional, defaults to user profile location if available)', nullable=True),
        'mileage': openapi.Schema(type=openapi.TYPE_INTEGER, description='Mileage (optional)', nullable=True),
        'color': openapi.Schema(type=openapi.TYPE_STRING, description='Color (optional)', nullable=True, enum=[choice[0] for choice in Vehicle._meta.get_field('color').choices]),
        'engine_volume': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description='Engine volume in liters (optional)', nullable=True),
        'engine_power': openapi.Schema(type=openapi.TYPE_INTEGER, description='Engine power in hp (optional)', nullable=True),
        'fuel_type': openapi.Schema(type=openapi.TYPE_STRING, description='Fuel type (optional)', nullable=True, enum=[choice[0] for choice in Vehicle._meta.get_field('fuel_type').choices]),
        'transmission': openapi.Schema(type=openapi.TYPE_STRING, description='Transmission type (optional)', nullable=True, enum=[choice[0] for choice in Vehicle._meta.get_field('transmission').choices]),
        'registration_country': openapi.Schema(type=openapi.TYPE_STRING, description='Registration country (optional)', nullable=True),
        'is_custom_cleared': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Customs cleared (optional)', nullable=True),
        'vin_code': openapi.Schema(type=openapi.TYPE_STRING, description='VIN code (optional)', nullable=True),
        'number_of_owners': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of owners (optional)', nullable=True),
        'uploaded_images': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY), description='List of images to upload (optional)', nullable=True),
        
        'body_type': openapi.Schema(type=openapi.TYPE_STRING, description='Car: Body type (optional)', nullable=True),
        'drive_type': openapi.Schema(type=openapi.TYPE_STRING, description='Car: Drive type (optional)', nullable=True),
        'technical_condition': openapi.Schema(type=openapi.TYPE_STRING, description='Car: Technical condition (optional)', nullable=True),
        'bike_type': openapi.Schema(type=openapi.TYPE_STRING, description='Motorcycle: Bike type (optional)', nullable=True),
        'seat_height': openapi.Schema(type=openapi.TYPE_INTEGER, description='Motorcycle: Seat height (mm) (optional)', nullable=True),
        'truck_load_capacity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Truck: Load capacity (kg) (optional)', nullable=True),
        'axle_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Truck: Axle count (optional)', nullable=True),
        'trailer_type': openapi.Schema(type=openapi.TYPE_STRING, description='Trailer: Trailer type (optional)', nullable=True),
        'trailer_load_capacity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Trailer: Load capacity (kg) (optional)', nullable=True),
        'specialization': openapi.Schema(type=openapi.TYPE_STRING, description='SpecialTech: Specialization (optional)', nullable=True),
        'weight': openapi.Schema(type=openapi.TYPE_INTEGER, description='SpecialTech: Weight (kg) (optional)', nullable=True),
        'seats': openapi.Schema(type=openapi.TYPE_INTEGER, description='Bus: Number of seats (optional)', nullable=True),
        'doors_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Bus: Number of doors (optional)', nullable=True),
        'boat_type': openapi.Schema(type=openapi.TYPE_STRING, description='WaterTransport: Boat type (optional)', nullable=True),
        'engine_type': openapi.Schema(type=openapi.TYPE_STRING, description='WaterTransport: Engine type (optional)', nullable=True),
        'hull_material': openapi.Schema(type=openapi.TYPE_STRING, description='WaterTransport: Hull material (optional)', nullable=True),
        'aircraft_type': openapi.Schema(type=openapi.TYPE_STRING, description='AirTransport: Aircraft type (optional)', nullable=True),
        'engine_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='AirTransport: Engine count (optional)', nullable=True),
        'max_altitude': openapi.Schema(type=openapi.TYPE_INTEGER, description='AirTransport: Max altitude (m) (optional)', nullable=True),
        'sleeping_places': openapi.Schema(type=openapi.TYPE_INTEGER, description='Motorhome: Sleeping places (optional)', nullable=True),
        'has_kitchen': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Motorhome: Has kitchen (optional)', nullable=True),
        'has_bathroom': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Motorhome: Has bathroom (optional)', nullable=True),
    }

    _create_request_body_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['vehicle_type', 'brand', 'model', 'year', 'price', 'currency', 'description'],
        properties={
            'vehicle_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of vehicle (e.g., car, motorcycle)', enum=list(VEHICLE_TYPES.keys())),
            **_common_vehicle_properties
        }
    )

    _update_request_body_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=_common_vehicle_properties
    )

    @swagger_auto_schema(
        request_body=_create_request_body_schema,
        responses={201: VehicleSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer(self, *args, **kwargs):
        """
        Ensures partial updates are handled correctly by setting partial=True
        for update and partial_update actions.
        """
        if self.action in ['update', 'partial_update']:
            kwargs['partial'] = True 
        return super().get_serializer(*args, **kwargs)

    @swagger_auto_schema(
        request_body=_update_request_body_schema,
        responses={200: VehicleSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=_update_request_body_schema,
        responses={200: VehicleSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['image'],
            properties={
                'image': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY, description='Image file to upload'),
            }
        ),
        responses={201: VehicleImageSerializer}
    )
    @action(detail=True, methods=['post'], url_path='add-image', permission_classes=[IsOwnerOrReadOnly])
    def add_image(self, request, pk=None):
        vehicle = self.get_object()
        serializer = VehicleImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vehicle=vehicle)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='my-vehicles', permission_classes=[IsAuthenticated])
    def my_vehicles(self, request):
        queryset = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={204: "No Content"}
    )
    @action(detail=True, methods=['delete'], url_path='delete-image/(?P<image_pk>[^/.]+)', permission_classes=[IsOwnerOrReadOnly])
    def delete_image(self, request, pk=None, image_pk=None):
        vehicle = self.get_object()
        try:
            image = VehicleImage.objects.get(pk=image_pk, vehicle=vehicle)
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except VehicleImage.DoesNotExist:
            return Response({"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND)