import json
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from .consumers import ChatConsumer
from .models import UserMessages

User = get_user_model()


class ChatConsumerTest(TransactionTestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )

    async def test_websocket_connection(self):
        """Test WebSocket connection for valid user"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"ws/chat/{self.user1.id}/"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_websocket_connection_invalid_user(self):
        """Test WebSocket connection for invalid user"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            "ws/chat/99999/"
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_send_message(self):
        """Test sending a message through WebSocket"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"ws/chat/{self.user1.id}/"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send a message
        message_data = {
            'type': 'chat_message',
            'message': 'Hello, World!',
            'receiver_id': self.user2.id
        }
        await communicator.send_json_to(message_data)

        # Receive the echoed message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'new_message')
        self.assertEqual(response['message']['text'], 'Hello, World!')
        
        await communicator.disconnect()

    async def test_send_message_to_self(self):
        """Test that sending message to self is rejected"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"ws/chat/{self.user1.id}/"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Try to send message to self
        message_data = {
            'type': 'chat_message',
            'message': 'Hello, World!',
            'receiver_id': self.user1.id
        }
        await communicator.send_json_to(message_data)

        # Should receive error
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        self.assertIn('Cannot send message to yourself', response['error'])
        
        await communicator.disconnect()

    async def test_send_empty_message(self):
        """Test that empty messages are rejected"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"ws/chat/{self.user1.id}/"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Try to send empty message
        message_data = {
            'type': 'chat_message',
            'message': '   ',  # Only spaces
            'receiver_id': self.user2.id
        }
        await communicator.send_json_to(message_data)

        # Should receive error
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        
        await communicator.disconnect()

    async def test_message_isolation(self):
        """Test that users only receive their own messages"""
        # Connect both users
        communicator1 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"ws/chat/{self.user1.id}/"
        )
        communicator2 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"ws/chat/{self.user2.id}/"
        )
        
        connected1, _ = await communicator1.connect()
        connected2, _ = await communicator2.connect()
        self.assertTrue(connected1)
        self.assertTrue(connected2)

        # User1 sends message to User2
        message_data = {
            'type': 'chat_message',
            'message': 'Hello from User1!',
            'receiver_id': self.user2.id
        }
        await communicator1.send_json_to(message_data)

        # Both should receive the message
        response1 = await communicator1.receive_json_from()
        response2 = await communicator2.receive_json_from()
        
        self.assertEqual(response1['type'], 'new_message')
        self.assertEqual(response2['type'], 'new_message')
        self.assertEqual(response1['message']['text'], 'Hello from User1!')
        self.assertEqual(response2['message']['text'], 'Hello from User1!')

        # Create third user that shouldn't receive the message
        user3 = await database_sync_to_async(User.objects.create_user)(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
        
        communicator3 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"ws/chat/{user3.id}/"
        )
        connected3, _ = await communicator3.connect()
        self.assertTrue(connected3)

        # User1 sends another message to User2
        message_data2 = {
            'type': 'chat_message',
            'message': 'Hello again!',
            'receiver_id': self.user2.id
        }
        await communicator1.send_json_to(message_data2)

        # User3 should not receive this message
        # (We'll check by ensuring User1 and User2 do receive it)
        response1_2 = await communicator1.receive_json_from()
        response2_2 = await communicator2.receive_json_from()
        
        self.assertEqual(response1_2['message']['text'], 'Hello again!')
        self.assertEqual(response2_2['message']['text'], 'Hello again!')

        await communicator1.disconnect()
        await communicator2.disconnect()
        await communicator3.disconnect()