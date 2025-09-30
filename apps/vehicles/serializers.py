from rest_framework import serializers
from django.db import transaction
from .models import (
    Vehicle, VehicleImage, Car, Motorcycle, Truck, Trailer,
    SpecialTech, Bus, WaterTransport, AirTransport, Motorhome
)
from apps.comments.serializers import CommentSerializer
from apps.reports.serializers import ReportSerializer

class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['id', 'image', 'vehicle']
        read_only_fields = ['vehicle']

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = (
            'body_type', 
            'drive_type', 
            'technical_condition'
        ) 

class MotorcycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motorcycle
        fields = (
            'bike_type', 
            'seat_height'
        )

class TruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = (
            'load_capacity', 
            'axle_count'
        )

class TrailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trailer
        fields = (
            'trailer_type', 
            'load_capacity'
        )

class SpecialTechSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialTech
        fields = (
            'specialization', 
            'weight'
        )

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = (
            'seats', 
            'doors_count'
        )

class WaterTransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterTransport
        fields = (
            'boat_type', 
            'engine_type', 
            'hull_material'
        )

class AirTransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirTransport
        fields = (
            'aircraft_type', 
            'engine_count', 
            'max_altitude'
        )

class MotorhomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motorhome
        fields = (
            'sleeping_places', 
            'has_kitchen', 
            'has_bathroom'
        )
        
class VehicleSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    motorcycle = MotorcycleSerializer(read_only=True)
    truck = TruckSerializer(read_only=True)
    trailer = TrailerSerializer(read_only=True)
    specialtech = SpecialTechSerializer(read_only=True)
    bus = BusSerializer(read_only=True)
    watertransport = WaterTransportSerializer(read_only=True)
    airtransport = AirTransportSerializer(read_only=True)
    motorhome = MotorhomeSerializer(read_only=True)
    
    user = serializers.PrimaryKeyRelatedField(read_only=True) 
    
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False),
        write_only=True,
        required=False
    )
    images = VehicleImageSerializer(many=True, read_only=True)

    body_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    drive_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    technical_condition = serializers.CharField(write_only=True, required=False, allow_blank=True)

    bike_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    seat_height = serializers.IntegerField(write_only=True, required=False)

    truck_load_capacity = serializers.IntegerField(write_only=True, required=False) 
    axle_count = serializers.IntegerField(write_only=True, required=False)

    trailer_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    trailer_load_capacity = serializers.IntegerField(write_only=True, required=False) 

    specialization = serializers.CharField(write_only=True, required=False, allow_blank=True)
    weight = serializers.IntegerField(write_only=True, required=False)

    seats = serializers.IntegerField(write_only=True, required=False)
    doors_count = serializers.IntegerField(write_only=True, required=False)

    boat_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    engine_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    hull_material = serializers.CharField(write_only=True, required=False, allow_blank=True)

    aircraft_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    engine_count = serializers.IntegerField(write_only=True, required=False)
    max_altitude = serializers.IntegerField(write_only=True, required=False)

    sleeping_places = serializers.IntegerField(write_only=True, required=False)
    has_kitchen = serializers.BooleanField(write_only=True, required=False)
    has_bathroom = serializers.BooleanField(write_only=True, required=False)


    class Meta:
        model = Vehicle
        fields = [
            'id', 'user', 'vehicle_type', 'brand', 'model', 'year', 'price', 'currency', 'description', 'location',
            'mileage', 'color', 'engine_volume', 'engine_power', 'fuel_type', 'transmission',
            'registration_country', 'is_custom_cleared', 'vin_code', 'number_of_owners', 'is_new',
            'is_active', 'views_count', 'created_at', 'updated_at', 'images',
            'uploaded_images',

            'car', 'motorcycle', 'truck', 'trailer', 'specialtech',
            'bus', 'watertransport', 'airtransport', 'motorhome',

            'body_type', 'drive_type', 'technical_condition',
            'bike_type', 'seat_height',
            'truck_load_capacity', 'axle_count',
            'trailer_type', 'trailer_load_capacity',
            'specialization', 'weight',
            'seats', 'doors_count',
            'boat_type', 'engine_type', 'hull_material',
            'aircraft_type', 'engine_count', 'max_altitude',
            'sleeping_places', 'has_kitchen', 'has_bathroom',
        ]

        read_only_fields = [
            'id', 'user', 'is_active', 'views_count', 'created_at', 'updated_at', 'images'
        ]

        extra_kwargs = {
            'mileage': {'required': False},
            'color': {'required': False, 'allow_blank': True},
            'engine_volume': {'required': False},
            'engine_power': {'required': False},
            'fuel_type': {'required': False, 'allow_blank': True},
            'transmission': {'required': False, 'allow_blank': True},
            'registration_country': {'required': False, 'allow_blank': True},
            'is_custom_cleared': {'required': False},
            'is_new': {'required': False},
            'vin_code': {'required': False, 'allow_blank': True},
            'number_of_owners': {'required': False},
        }

    def validate(self, data):
        request = self.context.get('request')
        user_location = None
        if request and request.user.is_authenticated:
            user_location = getattr(request.user, 'location', None)

        if self.instance is None:
            if not data.get('location') and not user_location:
                raise serializers.ValidationError(
                    {'location': 'Location is required if not provided in user profile.'}
                )
            elif not data.get('location') and user_location:
                data['location'] = user_location

            vehicle_type = data.get('vehicle_type')
            if not vehicle_type:
                raise serializers.ValidationError({"vehicle_type": "Vehicle type is required for creation."})

            if vehicle_type not in self.context['view'].VEHICLE_TYPES:
                raise serializers.ValidationError({"vehicle_type": "Invalid vehicle type provided."})

            if not request or not request.user or not request.user.is_authenticated:
                raise serializers.ValidationError({"user": "Authentication is required to create a vehicle."})

        else:
            if 'location' not in data and user_location and not self.instance.location:
                data['location'] = user_location
            elif data.get('location') is None and user_location:
                data['location'] = user_location


        return data

    @transaction.atomic
    def create(self, validated_data):
        vehicle_type = validated_data.pop('vehicle_type')
        uploaded_images = validated_data.pop('uploaded_images', [])

        subclass_model_info = self.context['view'].VEHICLE_TYPES.get(vehicle_type)
        if not subclass_model_info:
            raise serializers.ValidationError({"vehicle_type": "Invalid vehicle type provided."})

        subclass_model = subclass_model_info['model']

        base_vehicle_fields = {f.name for f in Vehicle._meta.fields}

        base_data_for_subclass = {k: v for k, v in validated_data.items() if k in base_vehicle_fields}
        base_data_for_subclass['vehicle_type'] = vehicle_type
        subclass_specific_data = {}

        if vehicle_type == 'car':
            subclass_specific_data['body_type'] = validated_data.pop('body_type', None)
            subclass_specific_data['drive_type'] = validated_data.pop('drive_type', None)
            subclass_specific_data['technical_condition'] = validated_data.pop('technical_condition', None)
        elif vehicle_type == 'motorcycle':
            subclass_specific_data['bike_type'] = validated_data.pop('bike_type', None)
            subclass_specific_data['seat_height'] = validated_data.pop('seat_height', None)
        elif vehicle_type == 'truck':
            subclass_specific_data['load_capacity'] = validated_data.pop('truck_load_capacity', None) 
            subclass_specific_data['axle_count'] = validated_data.pop('axle_count', None)
        elif vehicle_type == 'trailer':
            subclass_specific_data['trailer_type'] = validated_data.pop('trailer_type', None)
            subclass_specific_data['load_capacity'] = validated_data.pop('trailer_load_capacity', None) 
        elif vehicle_type == 'specialtech':
            subclass_specific_data['specialization'] = validated_data.pop('specialization', None)
            subclass_specific_data['weight'] = validated_data.pop('weight', None)
        elif vehicle_type == 'bus':
            subclass_specific_data['seats'] = validated_data.pop('seats', None)
            subclass_specific_data['doors_count'] = validated_data.pop('doors_count', None)
        elif vehicle_type == 'watertransport':
            subclass_specific_data['boat_type'] = validated_data.pop('boat_type', None)
            subclass_specific_data['engine_type'] = validated_data.pop('engine_type', None)
            subclass_specific_data['hull_material'] = validated_data.pop('hull_material', None)
        elif vehicle_type == 'airtransport':
            subclass_specific_data['aircraft_type'] = validated_data.pop('aircraft_type', None)
            subclass_specific_data['engine_count'] = validated_data.pop('engine_count', None)
            subclass_specific_data['max_altitude'] = validated_data.pop('max_altitude', None)
        elif vehicle_type == 'motorhome':
            subclass_specific_data['sleeping_places'] = validated_data.pop('sleeping_places', None)
            subclass_specific_data['has_kitchen'] = validated_data.pop('has_kitchen', None)
            subclass_specific_data['has_bathroom'] = validated_data.pop('has_bathroom', None)

        subclass_specific_data = {k: v for k, v in subclass_specific_data.items() if v is not None}
        
        final_creation_data = {**base_data_for_subclass, **subclass_specific_data}

        try:
            vehicle_instance = subclass_model.objects.create(**final_creation_data)

            for image_file in uploaded_images:
                VehicleImage.objects.create(vehicle=vehicle_instance, image=image_file)

            return vehicle_instance
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise serializers.ValidationError({"detail": f"Failed to create vehicle. Error: {e}"}) 
            
    @transaction.atomic
    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', []) 

        base_model_field_names = {field.name for field in Vehicle._meta.fields}
        
        base_vehicle_data = {}
        subclass_data = {}

        for key, value in validated_data.items():
            if key in base_model_field_names:
                base_vehicle_data[key] = value
            elif key == 'body_type':
                subclass_data['body_type'] = value
            elif key == 'drive_type':
                subclass_data['drive_type'] = value
            elif key == 'technical_condition':
                subclass_data['technical_condition'] = value
            elif key == 'bike_type':
                subclass_data['bike_type'] = value
            elif key == 'seat_height':
                subclass_data['seat_height'] = value
            elif key == 'truck_load_capacity':
                subclass_data['load_capacity'] = value
            elif key == 'axle_count':
                subclass_data['axle_count'] = value
            elif key == 'trailer_type':
                subclass_data['trailer_type'] = value
            elif key == 'trailer_load_capacity':
                subclass_data['load_capacity'] = value
            elif key == 'specialization':
                subclass_data['specialization'] = value
            elif key == 'weight':
                subclass_data['weight'] = value
            elif key == 'seats':
                subclass_data['seats'] = value
            elif key == 'doors_count':
                subclass_data['doors_count'] = value
            elif key == 'boat_type':
                subclass_data['boat_type'] = value
            elif key == 'engine_type':
                subclass_data['engine_type'] = value
            elif key == 'hull_material':
                subclass_data['hull_material'] = value
            elif key == 'aircraft_type':
                subclass_data['aircraft_type'] = value
            elif key == 'engine_count':
                subclass_data['engine_count'] = value
            elif key == 'max_altitude':
                subclass_data['max_altitude'] = value
            elif key == 'sleeping_places':
                subclass_data['sleeping_places'] = value
            elif key == 'has_kitchen':
                subclass_data['has_kitchen'] = value
            elif key == 'has_bathroom':
                subclass_data['has_bathroom'] = value
            elif key in ['car', 'motorcycle', 'truck', 'trailer', 'specialtech', 
                         'bus', 'watertransport', 'airtransport', 'motorhome', 
                         'images', 'created_at', 'updated_at', 'views_count', 'id']:
                pass 

        for attr, value in base_vehicle_data.items():
            setattr(instance, attr, value)
        instance.save(update_fields=base_vehicle_data.keys())

        current_vehicle_type_name = None
        subclass_instance = None
        for v_type_name, v_type_info in self.context['view'].VEHICLE_TYPES.items():
            if hasattr(instance, v_type_name) and getattr(instance, v_type_name) is not None:
                current_vehicle_type_name = v_type_name
                subclass_instance = getattr(instance, v_type_name)
                break

        if subclass_instance:
            for attr, value in subclass_data.items():
                setattr(subclass_instance, attr, value)
            subclass_instance.save(update_fields=subclass_data.keys())
        elif subclass_data:
            print(f"WARNING: Subclass data provided for update, but no existing subclass instance found for Vehicle ID: {instance.id}")

        for image_file in uploaded_images:
            VehicleImage.objects.create(vehicle=instance, image=image_file)

        return instance
    
class VehicleDetailSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    motorcycle = MotorcycleSerializer(read_only=True)
    truck = TruckSerializer(read_only=True)
    trailer = TrailerSerializer(read_only=True)
    specialtech = SpecialTechSerializer(read_only=True)
    bus = BusSerializer(read_only=True)
    watertransport = WaterTransportSerializer(read_only=True)
    airtransport = AirTransportSerializer(read_only=True)
    motorhome = MotorhomeSerializer(read_only=True)

    images = VehicleImageSerializer(many=True, read_only=True)
    
    comments = CommentSerializer(many=True, read_only=True)
    
    reports = ReportSerializer(many=True, read_only=True)

    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            'id', 'user', 'vehicle_type', 'brand', 'model', 'year', 'price', 'currency', 'description',
            'location', 'mileage', 'color', 'engine_volume', 'engine_power', 'fuel_type',
            'transmission', 'registration_country', 'is_custom_cleared', 'vin_code',
            'number_of_owners', 'is_new', 'is_active', 'views_count', 'created_at', 'updated_at',
            'images',
            'car', 'motorcycle', 'truck', 'trailer', 'specialtech',
            'bus', 'watertransport', 'airtransport', 'motorhome',
            'is_favorited', 'comments', 'reports',
        ]
        read_only_fields = [
            'id', 'user', 'is_active', 'views_count', 'created_at', 'updated_at'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False