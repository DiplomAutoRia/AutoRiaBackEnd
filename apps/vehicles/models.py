from django.db import models
from django.conf import settings


class Vehicle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    description = models.TextField()
    location = models.CharField(max_length=100)

    mileage = models.PositiveIntegerField(null=True, blank=True)
    color = models.CharField(max_length=30, null=True, blank=True)
    engine_volume = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    engine_power = models.PositiveIntegerField(null=True, blank=True)
    fuel_type = models.CharField(max_length=20, null=True, blank=True)
    transmission = models.CharField(max_length=20, null=True, blank=True)

    registration_country = models.CharField(max_length=50, null=True, blank=True)
    is_custom_cleared = models.BooleanField(null=True, blank=True)

    vin_code = models.CharField(max_length=30, null=True, blank=True, unique=True)

    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    number_of_owners = models.PositiveIntegerField(null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"


class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='vehicle_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.vehicle}"
    
    
class Car(Vehicle):
    body_type = models.CharField(max_length=30)
    drive_type = models.CharField(max_length=20)
    technical_condition = models.TextField(null=True, blank=True)


class Motorcycle(Vehicle):
    bike_type = models.CharField(max_length=30, null=True, blank=True)
    seat_height = models.PositiveIntegerField(null=True, blank=True)


class Truck(Vehicle):
    load_capacity = models.PositiveIntegerField()
    axle_count = models.PositiveIntegerField(null=True, blank=True)


class Trailer(Vehicle):
    trailer_type = models.CharField(max_length=30)
    load_capacity = models.PositiveIntegerField()


class SpecialTech(Vehicle):
    specialization = models.CharField(max_length=50)
    weight = models.PositiveIntegerField(null=True, blank=True)


class Bus(Vehicle):
    seats = models.PositiveIntegerField()
    doors_count = models.PositiveIntegerField(null=True, blank=True)


class WaterTransport(Vehicle):
    boat_type = models.CharField(max_length=50)
    engine_type = models.CharField(max_length=50)
    hull_material = models.CharField(max_length=50, null=True, blank=True)


class AirTransport(Vehicle):
    aircraft_type = models.CharField(max_length=50)
    engine_count = models.PositiveIntegerField()
    max_altitude = models.PositiveIntegerField(null=True, blank=True)


class Motorhome(Vehicle):
    sleeping_places = models.PositiveIntegerField()
    has_kitchen = models.BooleanField(default=False)
    has_bathroom = models.BooleanField(default=False)



