from django.db import models
from django.conf import settings
from apps.vehicles.models import Vehicle
from django.core.validators import MinValueValidator, MaxValueValidator

class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Author'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Vehicle'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Rating',
        help_text='Rating from 1 to 5'
    )
    text = models.TextField(verbose_name='Text')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

    def __str__(self):
        return f"{self.user} on {self.vehicle} ({self.rating})"
