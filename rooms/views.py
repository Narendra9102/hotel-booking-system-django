from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import datetime
from django.utils.dateparse import parse_datetime

from .models import Room
from .serializers import RoomSerializer, RoomListSerializer, AvailableRoomSerializer
from bookings.services import BookingService


# class RoomPagination(PageNumberPagination):
#     """Custom pagination for rooms"""
#     page_size = 20
#     page_size_query_param = 'page_size'
#     max_page_size = 100


class RoomListView(generics.ListAPIView):
    """
    List all available rooms with filters
    GET /api/rooms/
    
    Query Parameters:
    - room_type: Filter by room type (single, double, suite, etc.)
    - min_capacity: Minimum capacity required
    - max_hourly_rate: Maximum hourly rate
    - max_daily_rate: Maximum daily rate
    - status: Filter by status (default: available)
    """
    serializer_class = RoomListSerializer
    permission_classes = [permissions.IsAuthenticated]
    # pagination_class = RoomPagination

    def get_queryset(self):
        queryset = Room.objects.all()
        
        # Filter by status (default to available)
        status_filter = self.request.query_params.get('status', 'available')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by room type
        room_type = self.request.query_params.get('room_type')
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        
        # Filter by minimum capacity
        min_capacity = self.request.query_params.get('min_capacity')
        if min_capacity:
            try:
                queryset = queryset.filter(capacity__gte=int(min_capacity))
            except ValueError:
                pass
        
        # Filter by maximum hourly rate
        max_hourly_rate = self.request.query_params.get('max_hourly_rate')
        if max_hourly_rate:
            try:
                queryset = queryset.filter(hourly_rate__lte=float(max_hourly_rate))
            except ValueError:
                pass
        
        # Filter by maximum daily rate
        max_daily_rate = self.request.query_params.get('max_daily_rate')
        if max_daily_rate:
            try:
                queryset = queryset.filter(daily_rate__lte=float(max_daily_rate))
            except ValueError:
                pass
        
        # Filter by floor
        floor = self.request.query_params.get('floor')
        if floor:
            try:
                queryset = queryset.filter(floor=int(floor))
            except ValueError:
                pass
        
        return queryset.order_by('room_number')


class RoomDetailView(generics.RetrieveAPIView):
    """
    Retrieve detailed information about a specific room
    GET /api/rooms/{id}/
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_available_rooms(request):
    """
    Search for available rooms for a specific time period
    GET /api/rooms/search-available/
    
    Required Query Parameters:
    - start_time: ISO format datetime (YYYY-MM-DDTHH:MM:SS)
    - end_time: ISO format datetime (YYYY-MM-DDTHH:MM:SS)
    
    Optional Query Parameters:
    - room_type: Filter by room type
    - min_capacity: Minimum number of guests
    """
    # Get query parameters
    start_time_str = request.query_params.get('start_time')
    end_time_str = request.query_params.get('end_time')
    room_type = request.query_params.get('room_type')
    min_capacity = request.query_params.get('min_capacity')

    # Validate required parameters
    if not start_time_str or not end_time_str:
        return Response({
            'error': 'start_time and end_time are required',
            'example': 'start_time=2025-01-01T14:00:00&end_time=2025-01-01T18:00:00'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Parse datetime strings
    try:
    
        start_time = parse_datetime(start_time_str)
        end_time = parse_datetime(end_time_str)
        
        if start_time is None or end_time is None:
            raise ValueError("Invalid datetime")
        
        # Make timezone-aware if naive
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)
        if timezone.is_naive(end_time):
            end_time = timezone.make_aware(end_time)
            
    except (ValueError, TypeError):
        return Response({
            'error': 'Invalid datetime format. Use ISO format: YYYY-MM-DDTHH:MM:SS'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate time range
    if end_time <= start_time:
        return Response({
            'error': 'end_time must be after start_time'
        }, status=status.HTTP_400_BAD_REQUEST)

    if start_time < timezone.now():
        return Response({
            'error': 'start_time cannot be in the past'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Convert min_capacity to int if provided
    capacity_filter = None
    if min_capacity:
        try:
            capacity_filter = int(min_capacity)
        except ValueError:
            return Response({
                'error': 'min_capacity must be a valid integer'
            }, status=status.HTTP_400_BAD_REQUEST)

    # Get available rooms using the service
    available_rooms = BookingService.get_available_rooms(
        start_time=start_time,
        end_time=end_time,
        room_type=room_type,
        min_capacity=capacity_filter
    )

    # Serialize the results
    serializer = AvailableRoomSerializer(available_rooms, many=True)

    # Calculate duration for pricing context
    duration = end_time - start_time
    hours = duration.total_seconds() / 3600
    days = hours / 24

    return Response({
        'count': available_rooms.count(),
        'search_params': {
            'start_time': start_time,
            'end_time': end_time,
            'duration_hours': round(hours, 2),
            'duration_days': round(days, 2),
            'room_type': room_type,
            'min_capacity': capacity_filter
        },
        'rooms': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def room_types(request):
    """
    Get all available room types
    GET /api/rooms/types/
    """
    types = Room.ROOM_TYPES
    return Response({
        'room_types': [
            {'value': value, 'label': label}
            for value, label in types
        ]
    }, status=status.HTTP_200_OK)
