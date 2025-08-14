from rest_framework import serializers
from django.db.models import Q
from .models import UserMessages

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.username')

    class Meta:
        model = UserMessages
        fields = ['id', 'sender', 'sender_name', 'text', 'is_read', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()
    vehicle_title = serializers.ReadOnlyField(source='vehicle.title')
    
    class Meta:
        model = UserMessages
        fields = ['id', 'vehicle', 'vehicle_title', 'other_user', 'last_message', 'unread_count']
        
    def get_last_message(self, obj):
        last_msg = UserMessages.objects.filter(
            Q(pk=obj.pk) | Q(conversation=obj)
        ).latest('timestamp')
        return MessageSerializer(last_msg).data
        
    def get_unread_count(self, obj):
        return UserMessages.objects.filter(
            Q(pk=obj.pk) | Q(conversation=obj),
            receiver=self.context['request'].user,
            is_read=False
        ).count()
        
    def get_other_user(self, obj):
        if obj.sender == self.context['request'].user:
            return obj.receiver.username
        return obj.sender.username

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMessages
        fields = ['receiver', 'vehicle', 'conversation', 'text']