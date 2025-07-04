from django.db import models
from django.conf import settings
from apps.vehicles.models import Vehicle

class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='User'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Vehicle'
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Added at')

    class Meta:
        unique_together = ('user', 'vehicle')
        ordering = ['-added_at']
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return f"{self.user} -> {self.vehicle}"
