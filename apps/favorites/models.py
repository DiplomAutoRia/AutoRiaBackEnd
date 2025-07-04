from django.db import models
from django.conf import settings
from vehicles.models import Vehicle

class Favorite(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'vehicle')
        ordering = ['-added_at']

