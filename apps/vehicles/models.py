from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, ValidationError
from datetime import datetime

VEHICLE_TYPE_CHOICES = [
    ('car', 'Car'),
    ('motorcycle', 'Motorcycle'),
    ('truck', 'Truck'),
    ('trailer', 'Trailer'),
    ('specialtech', 'Special Tech'),
    ('bus', 'Bus'),
    ('watertransport', 'Water Transport'),
    ('airtransport', 'Air Transport'),
    ('motorhome', 'Motorhome'),
]

FUEL_TYPE_CHOICES = [
    ('petrol', 'Petrol'),
    ('diesel', 'Diesel'),
    ('electric', 'Electric'),
    ('hybrid', 'Hybrid'),
    ('gas', 'Gas'),
    ('other', 'Other'),
]
TRANSMISSION_CHOICES = [
    ('manual', 'Manual'),
    ('automatic', 'Automatic'),
    ('cvt', 'CVT'),
    ('robotic', 'Robotic'),
    ('other', 'Other'),
]
COLOR_CHOICES = [
    ('black', 'Black'),
    ('white', 'White'),
    ('gray', 'Gray'),
    ('red', 'Red'),
    ('blue', 'Blue'),
    ('green', 'Green'),
    ('other', 'Other'),
]

def current_year():
    return datetime.now().year

def max_year_validator(value):
    if value < 1900 or value > current_year() + 1:
        raise ValidationError(f'Year must be between 1900 and {current_year() + 1}.')

class Vehicle(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehicles',
        verbose_name='Owner',
        help_text='User who created the vehicle listing'
    )
    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES,
        default='car',
        verbose_name='Vehicle Type',
        help_text='Type of vehicle'
    )
    brand = models.CharField(max_length=50, verbose_name='Brand')
    model = models.CharField(max_length=50, verbose_name='Model')
    year = models.PositiveIntegerField(
        validators=[max_year_validator],
        verbose_name='Year',
        help_text='Production year (1900–next year)'
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Price',
        help_text='Positive price only'
    )
    currency = models.CharField(max_length=3, verbose_name='Currency')
    description = models.TextField(verbose_name='Description')
    location = models.CharField(max_length=100, verbose_name='Location')

    mileage = models.PositiveIntegerField(null=True, blank=True, verbose_name='Mileage')
    color = models.CharField(
        max_length=30, null=True, blank=True, choices=COLOR_CHOICES,
        verbose_name='Color'
    )
    engine_volume = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True,
        verbose_name='Engine volume (L)'
    )
    engine_power = models.PositiveIntegerField(null=True, blank=True, verbose_name='Engine power (hp)')
    fuel_type = models.CharField(
        max_length=20, null=True, blank=True,
        choices=FUEL_TYPE_CHOICES,
        verbose_name='Fuel type'
    )
    transmission = models.CharField(
        max_length=20, null=True, blank=True,
        choices=TRANSMISSION_CHOICES,
        verbose_name='Transmission'
    )

    registration_country = models.CharField(
        max_length=50, null=True, blank=True, verbose_name='Registration country'
    )
    is_custom_cleared = models.BooleanField(
        null=True, blank=True, verbose_name='Customs cleared'
    )
    vin_code = models.CharField(
        max_length=30, null=True, blank=True, unique=True,
        verbose_name='VIN code',
        help_text='Unique VIN code (may be empty)',
        validators=[
            RegexValidator(regex=r'^[A-HJ-NPR-Z0-9]{11,17}$', message='Invalid VIN')
        ]
    )
    is_new = models.BooleanField(default=False, verbose_name='Is New', help_text='Is vehicle new or used')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    views_count = models.PositiveIntegerField(default=0, verbose_name='View count')
    number_of_owners = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Number of owners'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='images',
        verbose_name='Vehicle'
    )
    image = models.ImageField(upload_to='vehicle_images/', verbose_name='Image')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Uploaded at')

    def __str__(self):
        return f"Image for {self.vehicle}"

class Car(Vehicle):
    body_type = models.CharField(max_length=30, verbose_name='Body type')
    drive_type = models.CharField(max_length=20, verbose_name='Drive type')
    technical_condition = models.TextField(null=True, blank=True, verbose_name='Technical condition')

class Motorcycle(Vehicle):
    bike_type = models.CharField(max_length=30, null=True, blank=True, verbose_name='Bike type')
    seat_height = models.PositiveIntegerField(null=True, blank=True, verbose_name='Seat height (mm)')

class Truck(Vehicle):
    load_capacity = models.PositiveIntegerField(verbose_name='Load capacity (kg)')
    axle_count = models.PositiveIntegerField(null=True, blank=True, verbose_name='Axle count')

class Trailer(Vehicle):
    trailer_type = models.CharField(max_length=30, verbose_name='Trailer type')
    load_capacity = models.PositiveIntegerField(verbose_name='Load capacity (kg)')

class SpecialTech(Vehicle):
    specialization = models.CharField(max_length=50, verbose_name='Specialization')
    weight = models.PositiveIntegerField(null=True, blank=True, verbose_name='Weight (kg)')

class Bus(Vehicle):
    seats = models.PositiveIntegerField(verbose_name='Number of seats')
    doors_count = models.PositiveIntegerField(null=True, blank=True, verbose_name='Number of doors')

class WaterTransport(Vehicle):
    boat_type = models.CharField(max_length=50, verbose_name='Boat type')
    engine_type = models.CharField(max_length=50, verbose_name='Engine type')
    hull_material = models.CharField(max_length=50, null=True, blank=True, verbose_name='Hull material')

class AirTransport(Vehicle):
    aircraft_type = models.CharField(max_length=50, verbose_name='Aircraft type')
    engine_count = models.PositiveIntegerField(verbose_name='Engine count')
    max_altitude = models.PositiveIntegerField(null=True, blank=True, verbose_name='Max altitude (m)')

class Motorhome(Vehicle):
    sleeping_places = models.PositiveIntegerField(verbose_name='Sleeping places')
    has_kitchen = models.BooleanField(default=False, verbose_name='Has kitchen')
    has_bathroom = models.BooleanField(default=False, verbose_name='Has bathroom')
