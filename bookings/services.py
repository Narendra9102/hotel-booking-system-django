from django.db.models import Q
from django.utils import timezone
from decimal import Decimal
from .models import Booking
from rooms.models import Room


class BookingService:
    """
    Service layer for booking business logic
    Handles availability checks, price calculations, and lifecycle management
    """

    @staticmethod
    def check_room_availability(room_id, start_time, end_time, exclude_booking_id=None):
        """
        Check if a room is available for the given time period
        
        Args:
            room_id: ID of the room to check
            start_time: Booking start datetime
            end_time: Booking end datetime
            exclude_booking_id: Optional booking ID to exclude from check (for updates)
        
        Returns:
            tuple: (is_available: bool, message: str)
        """
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return False, "Room does not exist"

        # Check room status
        if not room.is_available_for_booking():
            return False, f"Room {room.room_number} is currently {room.status}"

        # Check for overlapping bookings
        overlapping_query = Booking.objects.filter(
            room_id=room_id,
            status__in=['pending', 'confirmed', 'checked_in']
        ).filter(
            Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
        )

        if exclude_booking_id:
            overlapping_query = overlapping_query.exclude(id=exclude_booking_id)

        overlapping_bookings = overlapping_query.exists()

        if overlapping_bookings:
            return False, "Room is already booked for the selected time period"

        return True, "Room is available"

    @staticmethod
    def calculate_price(room, booking_type, start_time, end_time):
        """
        Calculate total price for a booking
        
        Args:
            room: Room instance
            booking_type: 'hourly' or 'daily'
            start_time: Booking start datetime
            end_time: Booking end datetime
        
        Returns:
            Decimal: Total price
        """
        duration = end_time - start_time
        hours = Decimal(str(duration.total_seconds() / 3600))

        if booking_type == 'hourly':
            total_price = hours * room.hourly_rate
        else:  # daily
            days = hours / Decimal('24')
            total_price = days * room.daily_rate

        # Round to 2 decimal places
        return total_price.quantize(Decimal('0.01'))

    @staticmethod
    def get_available_rooms(start_time, end_time, room_type=None, min_capacity=None):
        """
        Get list of available rooms for a time period with optional filters
        
        Args:
            start_time: Search start datetime
            end_time: Search end datetime
            room_type: Optional room type filter
            min_capacity: Optional minimum capacity filter
        
        Returns:
            QuerySet: Available rooms
        """
        # Start with available rooms
        rooms = Room.objects.filter(status='available')

        # Apply filters
        if room_type:
            rooms = rooms.filter(room_type=room_type)
        if min_capacity:
            rooms = rooms.filter(capacity__gte=min_capacity)

        # Get rooms with overlapping bookings
        booked_room_ids = Booking.objects.filter(
            status__in=['pending', 'confirmed', 'checked_in'],
            start_time__lt=end_time,
            end_time__gt=start_time
        ).values_list('room_id', flat=True).distinct()

        # Exclude booked rooms
        available_rooms = rooms.exclude(id__in=booked_room_ids)

        return available_rooms

    @staticmethod
    def perform_checkin(booking):
        """
        Perform check-in for a booking
        
        Args:
            booking: Booking instance
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not booking.can_checkin:
            if booking.status == 'checked_in':
                return False, "Booking is already checked in"
            elif booking.status == 'checked_out':
                return False, "Booking is already checked out"
            elif booking.status == 'cancelled':
                return False, "Cannot check in a cancelled booking"
            else:
                now = timezone.now()
                if now < booking.start_time - timezone.timedelta(hours=1):
                    return False, "Check-in is only allowed within 1 hour before start time"
                elif now > booking.end_time:
                    return False, "Booking time has expired"
                else:
                    return False, "Check-in not allowed for this booking"

        booking.status = 'checked_in'
        booking.actual_checkin_time = timezone.now()
        booking.save()

        return True, "Check-in successful"

    @staticmethod
    def perform_checkout(booking):
        """
        Perform check-out for a booking
        
        Args:
            booking: Booking instance
        
        Returns:
            tuple: (success: bool, message: str, extra_charges: Decimal)
        """
        if not booking.can_checkout:
            if booking.status == 'checked_out':
                return False, "Booking is already checked out", Decimal('0')
            else:
                return False, "Cannot check out this booking", Decimal('0')

        now = timezone.now()
        extra_charges = Decimal('0')

        # Calculate late checkout charges if applicable
        if now > booking.end_time:
            extra_duration = now - booking.end_time
            extra_hours = Decimal(str(extra_duration.total_seconds() / 3600))
            
            if booking.booking_type == 'hourly':
                extra_charges = extra_hours * booking.room.hourly_rate
            else:
                extra_charges = extra_hours * (booking.room.daily_rate / Decimal('24'))

            extra_charges = extra_charges.quantize(Decimal('0.01'))

        booking.status = 'checked_out'
        booking.actual_checkout_time = now
        if extra_charges > 0:
            booking.notes = f"Late checkout charges: {extra_charges}. " + (booking.notes or "")
        booking.save()

        return True, "Check-out successful", extra_charges

    @staticmethod
    def cancel_booking(booking, cancellation_reason=None):
        """
        Cancel a booking
        
        Args:
            booking: Booking instance
            cancellation_reason: Optional reason for cancellation
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not booking.can_cancel:
            if booking.status == 'cancelled':
                return False, "Booking is already cancelled"
            elif booking.status in ['checked_in', 'checked_out']:
                return False, "Cannot cancel a booking that has been checked in or out"
            else:
                return False, "Booking cannot be cancelled"

        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = cancellation_reason
        booking.save()

        return True, "Booking cancelled successfully"

    @staticmethod
    def expire_old_bookings():
        """
        Mark expired bookings (utility method for cron jobs)
        Updates bookings that have passed their end time but are still confirmed
        
        Returns:
            int: Number of bookings expired
        """
        now = timezone.now()
        expired_count = Booking.objects.filter(
            status='confirmed',
            end_time__lt=now
        ).update(status='expired')

        return expired_count