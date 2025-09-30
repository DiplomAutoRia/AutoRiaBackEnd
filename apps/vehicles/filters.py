import django_filters
from django.db.models import Q
from .models import (
    Vehicle
)

class VehicleFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(lookup_expr='icontains')
    model = django_filters.CharFilter(method='filter_multiple_models')
    year_min = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_max = django_filters.NumberFilter(field_name='year', lookup_expr='lte')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    mileage_min = django_filters.NumberFilter(field_name='mileage', lookup_expr='gte')
    mileage_max = django_filters.NumberFilter(field_name='mileage', lookup_expr='lte')
    
    fuel_type = django_filters.CharFilter(method='filter_multiple_fuel_types')
    transmission = django_filters.CharFilter(method='filter_multiple_transmissions')
    color = django_filters.CharFilter(method='filter_multiple_colors')
    
    currency = django_filters.CharFilter(method='filter_multiple_currencies')
    location = django_filters.CharFilter(method='filter_multiple_locations')
    registration_country = django_filters.CharFilter(method='filter_multiple_countries')
    is_new = django_filters.BooleanFilter()
    is_custom_cleared = django_filters.BooleanFilter()
    number_of_owners = django_filters.NumberFilter()

    vehicle_type = django_filters.CharFilter(method='filter_by_vehicle_type')

    body_type = django_filters.CharFilter(method='filter_car_body_type')
    drive_type = django_filters.CharFilter(method='filter_car_drive_type')
    technical_condition = django_filters.CharFilter(method='filter_car_technical_condition')

    bike_type = django_filters.CharFilter(method='filter_motorcycle_bike_type')
    seat_height_min = django_filters.NumberFilter(field_name='motorcycle__seat_height', lookup_expr='gte')
    seat_height_max = django_filters.NumberFilter(field_name='motorcycle__seat_height', lookup_expr='lte')

    truck_load_capacity_min = django_filters.NumberFilter(field_name='truck__load_capacity', lookup_expr='gte')
    truck_load_capacity_max = django_filters.NumberFilter(field_name='truck__load_capacity', lookup_expr='lte')
    axle_count = django_filters.NumberFilter(field_name='truck__axle_count')

    trailer_type = django_filters.CharFilter(method='filter_trailer_type')
    trailer_load_capacity_min = django_filters.NumberFilter(field_name='trailer__load_capacity', lookup_expr='gte')
    trailer_load_capacity_max = django_filters.NumberFilter(field_name='trailer__load_capacity', lookup_expr='lte')

    specialization = django_filters.CharFilter(method='filter_specialtech_specialization')
    weight_min = django_filters.NumberFilter(field_name='specialtech__weight', lookup_expr='gte')
    weight_max = django_filters.NumberFilter(field_name='specialtech__weight', lookup_expr='lte')

    seats_min = django_filters.NumberFilter(field_name='bus__seats', lookup_expr='gte')
    seats_max = django_filters.NumberFilter(field_name='bus__seats', lookup_expr='lte')
    doors_count_min = django_filters.NumberFilter(field_name='bus__doors_count', lookup_expr='gte')
    doors_count_max = django_filters.NumberFilter(field_name='bus__doors_count', lookup_expr='lte')

    boat_type = django_filters.CharFilter(method='filter_watertransport_boat_type')
    engine_type = django_filters.CharFilter(method='filter_watertransport_engine_type')
    hull_material = django_filters.CharFilter(method='filter_watertransport_hull_material')

    aircraft_type = django_filters.CharFilter(method='filter_airtransport_aircraft_type')
    engine_count_min = django_filters.NumberFilter(field_name='airtransport__engine_count', lookup_expr='gte')
    engine_count_max = django_filters.NumberFilter(field_name='airtransport__engine_count', lookup_expr='lte')
    max_altitude_min = django_filters.NumberFilter(field_name='airtransport__max_altitude', lookup_expr='gte')
    max_altitude_max = django_filters.NumberFilter(field_name='airtransport__max_altitude', lookup_expr='lte')

    sleeping_places_min = django_filters.NumberFilter(field_name='motorhome__sleeping_places', lookup_expr='gte')
    sleeping_places_max = django_filters.NumberFilter(field_name='motorhome__sleeping_places', lookup_expr='lte')
    has_kitchen = django_filters.BooleanFilter(field_name='motorhome__has_kitchen')
    has_bathroom = django_filters.BooleanFilter(field_name='motorhome__has_bathroom')

    def _split_and_filter(self, queryset, field_name, value):
        if not value:
            return queryset
        values = [v.strip() for v in value.split(',') if v.strip()]
        if not values:
            return queryset
        
        q_objects = Q()
        for v in values:
            q_objects |= Q(**{f"{field_name}__icontains": v})
        return queryset.filter(q_objects)

    def filter_multiple_models(self, queryset, name, value):
        return self._split_and_filter(queryset, 'model', value)

    def filter_multiple_currencies(self, queryset, name, value):
        return self._split_and_filter(queryset, 'currency', value)

    def filter_multiple_locations(self, queryset, name, value):
        return self._split_and_filter(queryset, 'location', value)
    
    def filter_multiple_countries(self, queryset, name, value):
        return self._split_and_filter(queryset, 'registration_country', value)

    def filter_multiple_fuel_types(self, queryset, name, value):
        return self._split_and_filter(queryset, 'fuel_type', value)

    def filter_multiple_transmissions(self, queryset, name, value):
        return self._split_and_filter(queryset, 'transmission', value)
        
    def filter_multiple_colors(self, queryset, name, value):
        return self._split_and_filter(queryset, 'color', value)

    def filter_by_vehicle_type(self, queryset, name, value):
        if not value:
            return queryset
        
        v_type = value.lower().strip()
        if v_type in ['car', 'motorcycle', 'truck', 'trailer', 'specialtech', 'bus', 'watertransport', 'airtransport', 'motorhome']:
            return queryset.filter(**{f"{v_type}__isnull": False})
        return queryset.none()
    
    def filter_car_body_type(self, queryset, name, value):
        return self._split_and_filter(queryset, 'car__body_type', value)
    
    def filter_car_drive_type(self, queryset, name, value):
        return self._split_and_filter(queryset, 'car__drive_type', value)
    
    def filter_car_technical_condition(self, queryset, name, value):
        return self._split_and_filter(queryset, 'car__technical_condition', value)

    def filter_motorcycle_bike_type(self, queryset, name, value):
        return self._split_and_filter(queryset, 'motorcycle__bike_type', value)

    def filter_trailer_type(self, queryset, name, value):
        return self._split_and_filter(queryset, 'trailer__trailer_type', value)

    def filter_truck_axle_count(self, queryset, name, value):
        return queryset.filter(truck__axle_count=value)
    
    def filter_specialtech_specialization(self, queryset, name, value):
        return self._split_and_filter(queryset, 'specialtech__specialization', value)

    def filter_bus_seats(self, queryset, name, value):
        return queryset.filter(bus__seats__exact=value)
        
    def filter_bus_doors_count(self, queryset, name, value):
        return queryset.filter(bus__doors_count__exact=value)

    def filter_watertransport_boat_type(self, queryset, name, value):
        return self._split_and_filter(queryset, 'watertransport__boat_type', value)

    def filter_watertransport_engine_type(self, queryset, name, value):
        return self._split_and_filter(queryset, 'watertransport__engine_type', value)
        
    def filter_watertransport_hull_material(self, queryset, name, value):
        return self._split_and_filter(queryset, 'watertransport__hull_material', value)

    def filter_airtransport_aircraft_type(self, queryset, name, value):
        return self._split_and_filter(queryset, 'airtransport__aircraft_type', value)
        
    def filter_motorhome_has_kitchen(self, queryset, name, value):
        return queryset.filter(motorhome__has_kitchen=value)

    def filter_motorhome_has_bathroom(self, queryset, name, value):
        return queryset.filter(motorhome__has_bathroom=value)

    class Meta:
        model = Vehicle
        fields = {
            'brand': ['icontains'],
            'model': ['icontains'],
            'year': ['gte', 'lte'],
            'price': ['gte', 'lte'],
            'mileage': ['gte', 'lte'],
            'engine_volume': ['gte', 'lte'],
            'engine_power': ['gte', 'lte'],
            'is_new': ['exact'],
            'is_custom_cleared': ['exact'],
            'number_of_owners': ['exact'],

            'fuel_type': ['icontains'],
            'transmission': ['icontains'],
            'color': ['icontains'],
        }