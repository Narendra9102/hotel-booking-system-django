from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from .models import Booking
from rooms.models import Room
from rooms.serializers import RoomListSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with validation
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'},
        label='Confirm Password'
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_username(self, value):
        """Check username uniqueness"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        """Check email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, 
        write_only=True,
        style={'input_type': 'password'}
    )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information
    """
    full_name = serializers.SerializerMethodField()
    total_bookings = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'full_name', 'total_bookings', 'date_joined']
        read_only_fields = ['username', 'date_joined']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_total_bookings(self, obj):
        return obj.bookings.count()


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating bookings with comprehensive validation
    """
    room_id = serializers.IntegerField(write_only=True)
    start_time = serializers.DateTimeField() 
    end_time = serializers.DateTimeField()

    class Meta:
        model = Booking
        fields = [
            'room_id', 'booking_type', 'start_time', 'end_time',
            'guest_name', 'guest_email', 'guest_phone', 'number_of_guests',
            'special_requests'
        ]

    def validate_room_id(self, value):
        """Validate room exists and is available"""
        try:
            room = Room.objects.get(id=value)
            if not room.is_available_for_booking():
                raise serializers.ValidationError(
                    f"Room {room.room_number} is not available for booking"
                )
            return value
        except Room.DoesNotExist:
            raise serializers.ValidationError("Room does not exist")

    def validate_start_time(self, value):
        """Validate start time is in the future"""
        if value < timezone.now():
            raise serializers.ValidationError("Start time cannot be in the past")
        return value

    def validate(self, attrs):
        """Comprehensive validation"""
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        # Make timezone-aware if naive
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)
            attrs['start_time'] = start_time
        
        if timezone.is_naive(end_time):
            end_time = timezone.make_aware(end_time)
            attrs['end_time'] = end_time
            
        booking_type = attrs.get('booking_type')
        room_id = attrs.get('room_id')
        number_of_guests = attrs.get('number_of_guests')

        # Validate time range
        if end_time <= start_time:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time"
            })

        # Validate duration based on booking type
        duration = end_time - start_time
        hours = duration.total_seconds() / 3600

        if booking_type == 'hourly':
            if hours < 1:
                raise serializers.ValidationError({
                    "booking_type": "Hourly bookings must be at least 1 hour"
                })
            if hours > 12:
                raise serializers.ValidationError({
                    "booking_type": "Hourly bookings cannot exceed 12 hours. Use daily booking instead."
                })
        elif booking_type == 'daily':
            if hours < 24:
                raise serializers.ValidationError({
                    "booking_type": "Daily bookings must be at least 24 hours"
                })

        # Validate room capacity
        room = Room.objects.get(id=room_id)
        if number_of_guests > room.capacity:
            raise serializers.ValidationError({
                "number_of_guests": f"Exceeds room capacity of {room.capacity}"
            })

        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            room_id=room_id,
            status__in=['pending', 'confirmed', 'checked_in']
        ).filter(
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if self.instance:
            overlapping = overlapping.exclude(id=self.instance.id)

        if overlapping.exists():
            raise serializers.ValidationError({
                "room": "Room is already booked for the selected time period"
            })

        return attrs

    def create(self, validated_data):
        """Create booking with calculated price"""
        room_id = validated_data.pop('room_id')
        room = Room.objects.get(id=room_id)
        user = self.context['request'].user

        # Calculate total price
        duration = validated_data['end_time'] - validated_data['start_time']
        hours = duration.total_seconds() / 3600

        if validated_data['booking_type'] == 'hourly':
            total_price = (Decimal(str(hours)) * room.hourly_rate).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        else:  # daily
            days = hours / 24
            total_price = (Decimal(str(days)) * room.daily_rate).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

        # Create booking
        booking = Booking.objects.create(
            user=user,
            room=room,
            total_price=total_price,
            status='confirmed',
            **validated_data
        )
        return booking


class BookingSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for booking with related data
    """
    room = RoomListSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)
    booking_type_display = serializers.CharField(
        source='get_booking_type_display', 
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', 
        read_only=True
    )
    duration_hours = serializers.FloatField(read_only=True)
    can_checkin = serializers.BooleanField(read_only=True)
    can_checkout = serializers.BooleanField(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'room', 'booking_type', 'booking_type_display',
            'start_time', 'end_time', 'duration_hours',
            'guest_name', 'guest_email', 'guest_phone', 'number_of_guests',
            'status', 'status_display', 'total_price',
            'actual_checkin_time', 'actual_checkout_time',
            'cancelled_at', 'cancellation_reason', 'special_requests',
            'notes', 'can_checkin', 'can_checkout', 'can_cancel',
            'created_at', 'updated_at'
        ]


class BookingListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing bookings
    """
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    room_type = serializers.CharField(source='room.get_room_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'room_number', 'room_type', 'booking_type',
            'start_time', 'end_time', 'status', 'status_display',
            'total_price', 'created_at'
        ]


class CancelBookingSerializer(serializers.Serializer):
    """
    Serializer for booking cancellation
    """
    cancellation_reason = serializers.CharField(
        required=False, 
        allow_blank=True,
        max_length=500
    )

