from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from rooms.models import Room


class Booking(models.Model):
    """
    Booking model for hourly and daily room bookings
    Implements strict validation and lifecycle management
    """
    BOOKING_TYPES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    # Core fields
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        db_index=True
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.PROTECT, 
        related_name='bookings',
        db_index=True
    )
    
    # Booking details
    booking_type = models.CharField(
        max_length=10, 
        choices=BOOKING_TYPES,
        db_index=True
    )
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    
    # Guest information
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)
    number_of_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    
    # Status and lifecycle
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    
    # Pricing
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Timestamps
    actual_checkin_time = models.DateTimeField(null=True, blank=True)
    actual_checkout_time = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    
    # Metadata
    special_requests = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['room', 'start_time', 'end_time']),
            models.Index(fields=['status', 'start_time']),
            models.Index(fields=['-created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F('start_time')),
                name='end_time_after_start_time'
            ),
        ]

    def __str__(self):
        return f"Booking #{self.id} - {self.room.room_number} by {self.user.username}"

    def clean(self):
        """Validation at model level"""
        errors = {}
        
        # Validate time range
        if self.end_time <= self.start_time:
            errors['end_time'] = "End time must be after start time"
        
        # Validate start time is not in the past
        if self.start_time < timezone.now():
            errors['start_time'] = "Start time cannot be in the past"
        
        # Validate guest capacity
        if hasattr(self, 'room') and self.number_of_guests > self.room.capacity:
            errors['number_of_guests'] = f"Exceeds room capacity of {self.room.capacity}"
        
        # Validate booking duration based on type
        duration = self.end_time - self.start_time
        hours = duration.total_seconds() / 3600
        
        if self.booking_type == 'hourly':
            if hours < 1:
                errors['booking_type'] = "Hourly bookings must be at least 1 hour"
            if hours > 12:
                errors['booking_type'] = "Hourly bookings cannot exceed 12 hours"
        elif self.booking_type == 'daily':
            if hours < 24:
                errors['booking_type'] = "Daily bookings must be at least 24 hours"
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to run validations"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duration_hours(self):
        """Calculate booking duration in hours"""
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 3600

    @property
    def duration_days(self):
        """Calculate booking duration in days"""
        return self.duration_hours / 24

    @property
    def is_active(self):
        """Check if booking is currently active"""
        return self.status in ['confirmed', 'checked_in']

    @property
    def can_checkin(self):
        """Check if booking can be checked in"""
        if self.status != 'confirmed':
            return False
        now = timezone.now()
        # Allow check-in 1 hour before start time
        return self.start_time - timezone.timedelta(hours=1) <= now <= self.end_time

    @property
    def can_checkout(self):
        """Check if booking can be checked out"""
        return self.status == 'checked_in'

    @property
    def can_cancel(self):
        """Check if booking can be cancelled"""
        if self.status in ['cancelled', 'checked_out', 'expired']:
            return False
        # Can only cancel before check-in
        return self.status in ['pending', 'confirmed']

    @property
    def is_upcoming(self):
        """Check if booking is upcoming"""
        return self.status in ['pending', 'confirmed'] and self.start_time > timezone.now()

    @property
    def is_past(self):
        """Check if booking is in the past"""
        return self.status in ['checked_out', 'cancelled', 'expired'] or self.end_time < timezone.now()
    
    