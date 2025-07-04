from django.db import models
from django.conf import settings
from vehicles.models import Car

class Comment(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


