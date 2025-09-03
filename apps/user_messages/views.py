from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F
from .models import UserMessages
from .serializers import MessageCreateSerializer, MessageSerializer, ConversationSerializer
from apps.users.utils import send_verification_email, send_verification_sms
from django.conf import settings

class MessageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserMessages.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receiver = serializer.validated_data['receiver']
        vehicle = serializer.validated_data.get('vehicle')
        conversation = serializer.validated_data.get('conversation')
        text = serializer.validated_data['text']

        if conversation:
            message = UserMessages.objects.create(
                sender=request.user,
                receiver=receiver,
                vehicle=conversation.vehicle,
                text=text,
                conversation=conversation
            )
        elif vehicle:
            existing_conversation = UserMessages.objects.filter(
                Q(sender=request.user, receiver=receiver, vehicle=vehicle, conversation__isnull=True) |
                Q(sender=receiver, receiver=request.user, vehicle=vehicle, conversation__isnull=True)
            ).first()

            if existing_conversation:
                message = UserMessages.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    vehicle=vehicle,
                    text=text,
                    conversation=existing_conversation
                )
            else:
                message = UserMessages.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    vehicle=vehicle,
                    text=text
                )
        else:
            return Response({"detail": "Either vehicle or conversation must be specified."}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Removed email notifications to avoid spam
        # self.send_notifications(message, request.user)

        headers = self.get_success_headers(serializer.data)
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED, headers=headers)

    def send_notifications(self, message, sender):
        receiver = message.receiver
        text_message = f"You have received a new message on AUTORIA regarding the listing: {message.vehicle.brand} {message.vehicle.model}.\nMessage text: {message.text}"
        
        conversation_id = message.conversation.id if message.conversation else message.id
        link = f"{settings.FRONTEND_URL}/messages/{conversation_id}/"

        if receiver.email and receiver.is_verified:
            try:
                send_verification_email(receiver.email, f"{text_message}\nView: {link}")
            except Exception as e:
                print(f"Error sending email notification: {e}")

        if receiver.phone_number and receiver.is_verified:
            try:
                send_verification_sms(receiver.phone_number, f"AUTORIA: You have a new message. View: {link}")
            except Exception as e:
                print(f"Error sending SMS notification: {e}")

    @action(detail=False, methods=['get'])
    def conversations(self, request):
        conversations = self.get_queryset().filter(conversation__isnull=True).order_by('-timestamp')
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path=r'conversation/(?P<conversation_id>\d+)')
    def conversation_detail(self, request, conversation_id=None):
        try:
            conversation_start_message = self.get_queryset().get(
                Q(pk=conversation_id, conversation__isnull=True)
            )
            messages = UserMessages.objects.filter(
                Q(pk=conversation_start_message.id) | Q(conversation=conversation_start_message)
            ).order_by('timestamp')

            messages.filter(receiver=request.user, is_read=False).update(is_read=True)

            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        except UserMessages.DoesNotExist:
            return Response({"detail": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)