import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import UserMessages
from .serializers import MessageSerializer
from asgiref.sync import sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"user_{self.user_id}"
        
        # Verify user authentication
        user = await self.get_user_by_id(int(self.user_id))
        if not user:
            await self.close()
            return
            
        self.user = user
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, 
            self.channel_name
        )

        await self.accept()
        
        print(f"WebSocket connection established for user {self.user_id}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat_message')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'mark_as_read':
                await self.handle_mark_as_read(text_data_json)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))

    async def handle_chat_message(self, data):
        message_text = data.get('message', '')
        receiver_id = data.get('receiver_id')
        vehicle_id = data.get('vehicle_id')
        conversation_id = data.get('conversation_id')

        if not message_text or not receiver_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Message and receiver_id are required'
            }))
            return

        # Validate that sender is not trying to send to themselves
        if int(self.user_id) == int(receiver_id):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Cannot send message to yourself'
            }))
            return

        # Validate message length
        if len(message_text.strip()) > 1000:  # Max message length
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Message too long (max 1000 characters)'
            }))
            return

        # Save message to database
        message = await self.create_message(
            sender_id=int(self.user_id),
            receiver_id=receiver_id,
            text=message_text,
            vehicle_id=vehicle_id,
            conversation_id=conversation_id
        )

        if message:
            # Serialize message
            message_data = await self.serialize_message(message)
            
            # Send message to both sender and receiver, but only if they should see it
            sender_group = f"user_{self.user_id}"
            receiver_group = f"user_{receiver_id}"
            
            # Send to sender (who sent the message)
            await self.channel_layer.group_send(
                sender_group,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )
            
            # Send to receiver (who should receive the message)
            if sender_group != receiver_group:  # Avoid duplicate send to same user
                await self.channel_layer.group_send(
                    receiver_group,
                    {
                        'type': 'chat_message',
                        'message': message_data
                    }
                )
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Failed to create message'
            }))

    async def handle_mark_as_read(self, data):
        conversation_id = data.get('conversation_id')
        if conversation_id:
            unread_count = await self.mark_messages_as_read(conversation_id, int(self.user_id))
            
            if unread_count > 0:
                # Notify about read status update to current user
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'messages_read',
                        'conversation_id': conversation_id
                    }
                )
            
            print(f"User {self.user_id} marked {unread_count} messages as read in conversation {conversation_id}")

    async def chat_message(self, event):
        message = event['message']
        
        # Verify user should receive this message
        current_user_id = int(self.user_id)
        message_sender_id = message.get('sender', {}).get('id')
        message_receiver_id = message.get('receiver', {}).get('id')
        
        # Only send message if current user is either sender or receiver
        if current_user_id == message_sender_id or current_user_id == message_receiver_id:
            await self.send(text_data=json.dumps({
                'type': 'new_message',
                'message': message
            }))

    async def messages_read(self, event):
        # Only send read notification to the user who marked as read
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'conversation_id': event['conversation_id']
        }))

    @database_sync_to_async
    def create_message(self, sender_id, receiver_id, text, vehicle_id=None, conversation_id=None):
        try:
            sender = User.objects.get(id=sender_id)
            receiver = User.objects.get(id=receiver_id)
            
            kwargs = {
                'sender': sender,
                'receiver': receiver,
                'text': text
            }
            
            if conversation_id:
                try:
                    conversation = UserMessages.objects.get(id=conversation_id, conversation__isnull=True)
                    kwargs['conversation'] = conversation
                    kwargs['vehicle'] = conversation.vehicle
                except UserMessages.DoesNotExist:
                    return None
            elif vehicle_id:
                from apps.vehicles.models import Vehicle
                try:
                    vehicle = Vehicle.objects.get(id=vehicle_id)
                    kwargs['vehicle'] = vehicle
                    
                    # Check for existing conversation
                    existing_conversation = UserMessages.objects.filter(
                        sender__in=[sender, receiver],
                        receiver__in=[sender, receiver],
                        vehicle=vehicle,
                        conversation__isnull=True
                    ).first()
                    
                    if existing_conversation:
                        kwargs['conversation'] = existing_conversation
                        
                except Vehicle.DoesNotExist:
                    return None
            
            return UserMessages.objects.create(**kwargs)
            
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def serialize_message(self, message):
        return MessageSerializer(message).data

    @database_sync_to_async
    def mark_messages_as_read(self, conversation_id, user_id):
        try:
            conversation = UserMessages.objects.get(id=conversation_id, conversation__isnull=True)
            
            # Mark all related messages as read in one query
            unread_count = UserMessages.objects.filter(
                Q(conversation=conversation) | Q(pk=conversation.id),
                receiver_id=user_id,
                is_read=False
            ).update(is_read=True)
            
            # Log for debugging
            if unread_count > 0:
                print(f"Marked {unread_count} messages as read for user {user_id} in conversation {conversation_id}")
                
            return unread_count
            
        except UserMessages.DoesNotExist:
            print(f"Conversation {conversation_id} not found for user {user_id}")
            return 0

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None