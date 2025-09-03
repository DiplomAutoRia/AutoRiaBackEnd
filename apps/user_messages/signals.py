from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import UserMessages
from .serializers import MessageSerializer

@receiver(post_save, sender=UserMessages)
def message_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        message_data = MessageSerializer(instance).data
        
        # Send to both sender and receiver
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.sender.id}",
            {
                'type': 'chat_message',
                'message': message_data
            }
        )
        
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.receiver.id}",
            {
                'type': 'chat_message',
                'message': message_data
            }
        )