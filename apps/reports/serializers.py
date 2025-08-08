from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Report
        fields = ['id', 'user', 'vehicle', 'reason', 'description', 'created_at']
        read_only_fields = ['user', 'vehicle', 'created_at']

class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['reason', 'description']