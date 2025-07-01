from django.db import models
from django.conf import settings
from cars.models import Car

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.SET_NULL,
        related_name='messages',
        null=True,
        blank=True
    )
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Повідомлення від {self.sender.email} до {self.receiver.email} — {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
