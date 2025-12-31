from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import Booking
from rooms.models import Room


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set additional fields if provided
            if request.POST.get('first_name'):
                user.first_name = request.POST.get('first_name')
            if request.POST.get('last_name'):
                user.last_name = request.POST.get('last_name')
            if request.POST.get('email'):
                user.email = request.POST.get('email')
            user.save()
            
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')
    return redirect('dashboard')


# ============================================================================
# DASHBOARD VIEW
# ============================================================================

@login_required
def dashboard_view(request):
    """User dashboard with statistics"""
    user = request.user
    now = timezone.now()
    
    # Get booking statistics
    total_bookings = Booking.objects.filter(user=user).count()
    
    upcoming_bookings = Booking.objects.filter(
        user=user,
        status__in=['pending', 'confirmed'],
        start_time__gt=now
    ).count()
    
    active_bookings = Booking.objects.filter(
        user=user,
        status__in=['confirmed', 'checked_in'],
        start_time__lte=now,
        end_time__gte=now
    ).count()
    
    past_bookings = Booking.objects.filter(
        user=user,
        status__in=['checked_out', 'cancelled']
    ).count()
    
    # Get recent bookings
    recent_bookings = Booking.objects.filter(
        user=user
    ).select_related('room').order_by('-created_at')[:5]
    
    context = {
        'total_bookings': total_bookings,
        'upcoming_bookings': upcoming_bookings,
        'active_bookings': active_bookings,
        'past_bookings': past_bookings,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'dashboard.html', context)


# ============================================================================
# ROOM VIEWS
# ============================================================================

@login_required
def rooms_view(request):
    """List all available rooms with filters"""
    rooms = Room.objects.filter(status='available')
    
    # Apply filters
    room_type = request.GET.get('room_type')
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    
    min_capacity = request.GET.get('min_capacity')
    if min_capacity:
        try:
            rooms = rooms.filter(capacity__gte=int(min_capacity))
        except ValueError:
            pass
    
    max_hourly_rate = request.GET.get('max_hourly_rate')
    if max_hourly_rate:
        try:
            rooms = rooms.filter(hourly_rate__lte=float(max_hourly_rate))
        except ValueError:
            pass
    
    max_daily_rate = request.GET.get('max_daily_rate')
    if max_daily_rate:
        try:
            rooms = rooms.filter(daily_rate__lte=float(max_daily_rate))
        except ValueError:
            pass
    
    context = {
        'rooms': rooms.order_by('room_number')
    }
    
    return render(request, 'rooms.html', context)


@login_required
def book_room_view(request, room_id):
    """Book a specific room"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        # Handle booking creation
        try:
            booking_type = request.POST.get('booking_type')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            guest_name = request.POST.get('guest_name')
            guest_email = request.POST.get('guest_email')
            guest_phone = request.POST.get('guest_phone')
            number_of_guests = request.POST.get('number_of_guests')
            special_requests = request.POST.get('special_requests', '')
            
            # Create booking (you can add more validation here)
            from datetime import datetime
            from .services import BookingService
            from decimal import Decimal
            
            start_dt = parse_datetime(start_time)
            end_dt = parse_datetime(end_time)

            if timezone.is_naive(start_dt):
                start_dt = timezone.make_aware(start_dt)

            if timezone.is_naive(end_dt):
                end_dt = timezone.make_aware(end_dt)
            
            # Check availability
            is_available, message = BookingService.check_room_availability(
                room_id, start_dt, end_dt
            )
            
            if not is_available:
                messages.error(request, message)
                return redirect('book_room', room_id=room_id)
            
            # Calculate price
            total_price = BookingService.calculate_price(
                room, booking_type, start_dt, end_dt
            )
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                room=room,
                booking_type=booking_type,
                start_time=start_dt,
                end_time=end_dt,
                guest_name=guest_name,
                guest_email=guest_email,
                guest_phone=guest_phone,
                number_of_guests=int(number_of_guests),
                total_price=total_price,
                special_requests=special_requests,
                status='confirmed'
            )
            
            messages.success(request, f'Booking confirmed! Booking ID: #{booking.id}')
            return redirect('booking_detail', booking_id=booking.id)
            
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('book_room', room_id=room_id)
    
    context = {
        'room': room
    }
    
    return render(request, 'book_room.html', context)


# ============================================================================
# BOOKING VIEWS
# ============================================================================

@login_required
def my_bookings_view(request):
    """List user's bookings with filters"""
    bookings = Booking.objects.filter(user=request.user).select_related('room')
    
    # Apply filter
    filter_type = request.GET.get('filter', 'all')
    now = timezone.now()
    
    if filter_type == 'upcoming':
        bookings = bookings.filter(
            status__in=['pending', 'confirmed'],
            start_time__gt=now
        )
    elif filter_type == 'active':
        bookings = bookings.filter(
            status__in=['confirmed', 'checked_in'],
            start_time__lte=now,
            end_time__gte=now
        )
    elif filter_type == 'past':
        bookings = bookings.filter(
            Q(status__in=['checked_out', 'cancelled', 'expired']) |
            Q(end_time__lt=now)
        )
    
    bookings = bookings.order_by('-created_at')
    
    context = {
        'bookings': bookings,
        'filter': filter_type
    }
    
    return render(request, 'my_bookings.html', context)


@login_required
def booking_detail_view(request, booking_id):
    """View booking details"""
    booking = get_object_or_404(
        Booking.objects.select_related('room'), 
        id=booking_id, 
        user=request.user
    )
    
    context = {
        'booking': booking
    }
    
    return render(request, 'booking_detail.html', context)


@login_required
def checkin_booking_view(request, booking_id):
    """Check-in to a booking"""
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        from .services import BookingService
        success, message = BookingService.perform_checkin(booking)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    
    return redirect('my_bookings')


@login_required
def checkout_booking_view(request, booking_id):
    """Check-out from a booking"""
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        from .services import BookingService
        success, message, extra_charges = BookingService.perform_checkout(booking)
        
        if success:
            if extra_charges > 0:
                messages.warning(request, f'{message} Extra charges: ₹{extra_charges}')
            else:
                messages.success(request, message)
        else:
            messages.error(request, message)
    
    return redirect('my_bookings')


@login_required
def cancel_booking_view(request, booking_id):
    """Cancel a booking"""
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        from .services import BookingService
        success, message = BookingService.cancel_booking(booking)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    
    return redirect('my_bookings')


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'profile.html')


# ============================================================================
# HOME VIEW
# ============================================================================

def home_view(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')