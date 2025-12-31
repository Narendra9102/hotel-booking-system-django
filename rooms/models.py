from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Room(models.Model):
    """
    Room model representing hotel rooms available for booking
    """
    ROOM_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
        ('deluxe', 'Deluxe'),
        ('presidential', 'Presidential Suite'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
    ]

    room_number = models.CharField(
        max_length=10, 
        unique=True, 
        db_index=True,
        help_text="Unique room identifier"
    )
    room_type = models.CharField(
        max_length=20, 
        choices=ROOM_TYPES,
        db_index=True
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of guests"
    )
    hourly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Rate per hour"
    )
    daily_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Rate per day (24 hours)"
    )
    floor = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Floor number"
    )
    amenities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of amenities (WiFi, TV, AC, etc.)"
    )
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        db_index=True
    )
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['room_number']
        indexes = [
            models.Index(fields=['room_type', 'status']),
            models.Index(fields=['status', 'room_number']),
        ]

    def __str__(self):
        return f"Room {self.room_number} - {self.get_room_type_display()}"

    def is_available_for_booking(self):
        """Check if room status allows booking"""
        return self.status == 'available'
    
    