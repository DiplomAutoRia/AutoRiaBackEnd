from django.db import models
from django.conf import settings
from apps.vehicles.models import Vehicle

class UserMessages(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Sender'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Receiver'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        related_name='messages',
        null=True,
        blank=True,
        verbose_name='Vehicle'
    )
    text = models.TextField(verbose_name='Text')
    is_read = models.BooleanField(default=False, verbose_name='Is read')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"From {self.sender} to {self.receiver} ({self.timestamp})"
