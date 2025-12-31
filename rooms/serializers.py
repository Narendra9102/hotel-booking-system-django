from rest_framework import serializers
from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    """
    Serializer for Room model with all details
    """
    room_type_display = serializers.CharField(
        source='get_room_type_display', 
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', 
        read_only=True
    )

    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'room_type', 'room_type_display',
            'capacity', 'hourly_rate', 'daily_rate', 'floor',
            'amenities', 'description', 'status', 'status_display',
            'image_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoomListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing rooms
    """
    room_type_display = serializers.CharField(
        source='get_room_type_display', 
        read_only=True
    )

    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'room_type', 'room_type_display',
            'capacity', 'hourly_rate', 'daily_rate', 'status', 'image_url'
        ]


class AvailableRoomSerializer(serializers.ModelSerializer):
    """
    Serializer for available rooms with availability context
    """
    room_type_display = serializers.CharField(
        source='get_room_type_display', 
        read_only=True
    )
    is_available = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'room_type', 'room_type_display',
            'capacity', 'hourly_rate', 'daily_rate', 'floor',
            'amenities', 'description', 'image_url', 'is_available'
        ]