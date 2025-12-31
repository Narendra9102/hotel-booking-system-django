"""
Django Management Command to Populate Sample Room Data

Save this file as: rooms/management/commands/populate_rooms.py

Directory structure:
rooms/
  management/
    __init__.py
    commands/
      __init__.py
      populate_rooms.py

Run with: python manage.py populate_rooms
"""

from django.core.management.base import BaseCommand
from rooms.models import Room
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with sample hotel rooms'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample rooms...')
        
        # Clear existing rooms (optional - comment out if you want to keep existing)
        Room.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing rooms'))

        sample_rooms = [
            # Single Rooms (Floor 1)
            {
                'room_number': '101',
                'room_type': 'single',
                'capacity': 1,
                'hourly_rate': Decimal('300.00'),
                'daily_rate': Decimal('5000.00'),
                'floor': 1,
                'amenities': ['WiFi', 'TV', 'AC', 'Work Desk'],
                'description': 'Cozy single room perfect for solo travelers',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800'
            },
            {
                'room_number': '102',
                'room_type': 'single',
                'capacity': 1,
                'hourly_rate': Decimal('300.00'),
                'daily_rate': Decimal('5000.00'),
                'floor': 1,
                'amenities': ['WiFi', 'TV', 'AC', 'Work Desk'],
                'description': 'Comfortable single room with city view',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800'
            },
            {
                'room_number': '103',
                'room_type': 'single',
                'capacity': 1,
                'hourly_rate': Decimal('300.00'),
                'daily_rate': Decimal('5000.00'),
                'floor': 1,
                'amenities': ['WiFi', 'TV', 'AC'],
                'description': 'Budget-friendly single room',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800'
            },

            # Double Rooms (Floor 2)
            {
                'room_number': '201',
                'room_type': 'double',
                'capacity': 2,
                'hourly_rate': Decimal('500.00'),
                'daily_rate': Decimal('8000.00'),
                'floor': 2,
                'amenities': ['WiFi', 'TV', 'AC', 'Mini Bar', 'Coffee Maker'],
                'description': 'Spacious double room with queen bed',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800'
            },
            {
                'room_number': '202',
                'room_type': 'double',
                'capacity': 2,
                'hourly_rate': Decimal('500.00'),
                'daily_rate': Decimal('8000.00'),
                'floor': 2,
                'amenities': ['WiFi', 'TV', 'AC', 'Mini Bar', 'Balcony'],
                'description': 'Double room with private balcony',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800'
            },
            {
                'room_number': '203',
                'room_type': 'double',
                'capacity': 2,
                'hourly_rate': Decimal('500.00'),
                'daily_rate': Decimal('8000.00'),
                'floor': 2,
                'amenities': ['WiFi', 'TV', 'AC', 'Mini Bar'],
                'description': 'Modern double room with city view',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800'
            },
            {
                'room_number': '204',
                'room_type': 'double',
                'capacity': 2,
                'hourly_rate': Decimal('500.00'),
                'daily_rate': Decimal('8000.00'),
                'floor': 2,
                'amenities': ['WiFi', 'TV', 'AC', 'Mini Bar', 'Coffee Maker'],
                'description': 'Elegant double room with work area',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800'
            },
            {
                'room_number': '205',
                'room_type': 'double',
                'capacity': 2,
                'hourly_rate': Decimal('500.00'),
                'daily_rate': Decimal('8000.00'),
                'floor': 2,
                'amenities': ['WiFi', 'TV', 'AC', 'Mini Bar'],
                'description': 'Comfortable double room',
                'status': 'maintenance',  # One room under maintenance
                'image_url': 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800'
            },

            # Suite Rooms (Floor 3)
            {
                'room_number': '301',
                'room_type': 'suite',
                'capacity': 3,
                'hourly_rate': Decimal('800.00'),
                'daily_rate': Decimal('12000.00'),
                'floor': 3,
                'amenities': ['WiFi', 'TV', 'AC', 'Mini Bar', 'Coffee Maker', 'Living Room', 'Balcony', 'Bathtub'],
                'description': 'Luxurious suite with separate living area',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800'
            },
            {
                'room_number': '302',
                'room_type': 'suite',
                'capacity': 3,
                'hourly_rate': Decimal('800.00'),
                'daily_rate': Decimal('12000.00'),
                'floor': 3,
                'amenities': ['WiFi', 'TV', 'AC', 'Mini Bar', 'Coffee Maker', 'Living Room', 'City View'],
                'description': 'Premium suite with panoramic views',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800'
            },
            {
                'room_number': '303',
                'room_type': 'suite',
                'capacity': 4,
                'hourly_rate': Decimal('800.00'),
                'daily_rate': Decimal('12000.00'),
                'floor': 3,
                'amenities': ['WiFi', 'TV', 'AC', 'Mini Bar', 'Coffee Maker', 'Living Room', 'Balcony', 'Bathtub', 'Dining Area'],
                'description': 'Family suite with extra space',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800'
            },

            # Deluxe Rooms (Floor 4)
            {
                'room_number': '401',
                'room_type': 'deluxe',
                'capacity': 3,
                'hourly_rate': Decimal('1000.00'),
                'daily_rate': Decimal('15000.00'),
                'floor': 4,
                'amenities': ['WiFi', 'Smart TV', 'AC', 'Premium Mini Bar', 'Espresso Machine', 'Living Area', 'Balcony', 'Jacuzzi', 'Premium Toiletries'],
                'description': 'Deluxe room with premium amenities',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800'
            },
            {
                'room_number': '402',
                'room_type': 'deluxe',
                'capacity': 3,
                'hourly_rate': Decimal('1000.00'),
                'daily_rate': Decimal('15000.00'),
                'floor': 4,
                'amenities': ['WiFi', 'Smart TV', 'AC', 'Premium Mini Bar', 'Espresso Machine', 'Living Area', 'City View', 'Jacuzzi'],
                'description': 'Deluxe room with stunning city views',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800'
            },
            {
                'room_number': '403',
                'room_type': 'deluxe',
                'capacity': 4,
                'hourly_rate': Decimal('1000.00'),
                'daily_rate': Decimal('15000.00'),
                'floor': 4,
                'amenities': ['WiFi', 'Smart TV', 'AC', 'Premium Mini Bar', 'Espresso Machine', 'Living Area', 'Balcony', 'Jacuzzi', 'Walk-in Closet'],
                'description': 'Spacious deluxe room with modern design',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800'
            },

            # Presidential Suites (Floor 5)
            {
                'room_number': '501',
                'room_type': 'presidential',
                'capacity': 6,
                'hourly_rate': Decimal('2000.00'),
                'daily_rate': Decimal('30000.00'),
                'floor': 5,
                'amenities': [
                    'WiFi', 'Smart TV', 'AC', 'Premium Mini Bar', 'Espresso Machine', 
                    'Living Room', 'Dining Room', 'Balcony', 'Jacuzzi', 'Premium Toiletries',
                    'Butler Service', 'Kitchen', 'Private Elevator', 'Panoramic View'
                ],
                'description': 'Presidential suite with world-class luxury',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800'
            },
            {
                'room_number': '502',
                'room_type': 'presidential',
                'capacity': 8,
                'hourly_rate': Decimal('2000.00'),
                'daily_rate': Decimal('30000.00'),
                'floor': 5,
                'amenities': [
                    'WiFi', 'Smart TV', 'AC', 'Premium Mini Bar', 'Espresso Machine',
                    'Living Room', 'Dining Room', 'Balcony', 'Jacuzzi', 'Premium Toiletries',
                    'Butler Service', 'Kitchen', 'Private Elevator', 'Panoramic View', 'Home Theater'
                ],
                'description': 'Grand presidential suite with entertainment area',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800'
            },

            # Additional rooms for variety
            {
                'room_number': '206',
                'room_type': 'double',
                'capacity': 2,
                'hourly_rate': Decimal('500.00'),
                'daily_rate': Decimal('8000.00'),
                'floor': 2,
                'amenities': ['WiFi', 'TV', 'AC', 'Mini Bar'],
                'description': 'Standard double room',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800'
            },
            {
                'room_number': '104',
                'room_type': 'single',
                'capacity': 1,
                'hourly_rate': Decimal('300.00'),
                'daily_rate': Decimal('5000.00'),
                'floor': 1,
                'amenities': ['WiFi', 'TV', 'AC'],
                'description': 'Economy single room',
                'status': 'available',
                'image_url': 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800'
            },
        ]

        created_count = 0
        for room_data in sample_rooms:
            room, created = Room.objects.get_or_create(
                room_number=room_data['room_number'],
                defaults=room_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {room.room_number} - {room.get_room_type_display()}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Already exists: {room.room_number}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Successfully created {created_count} rooms!')
        )
        
        # Display summary
        self.stdout.write('\n📊 Room Summary:')
        for room_type, label in Room.ROOM_TYPES:
            count = Room.objects.filter(room_type=room_type, status='available').count()
            self.stdout.write(f'  {label}: {count} available')
        
        total = Room.objects.filter(status='available').count()
        self.stdout.write(self.style.SUCCESS(f'\n✨ Total Available Rooms: {total}'))