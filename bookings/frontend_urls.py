from django.urls import path
from . import frontend_views

urlpatterns = [
    # Home
    path('', frontend_views.home_view, name='home'),
    
    # Authentication
    path('register/', frontend_views.register_view, name='register'),
    path('login/', frontend_views.login_view, name='login'),
    path('logout/', frontend_views.logout_view, name='logout'),
    path('profile/', frontend_views.profile_view, name='profile'),
    
    # Dashboard
    path('dashboard/', frontend_views.dashboard_view, name='dashboard'),
    
    # Rooms
    path('rooms/', frontend_views.rooms_view, name='rooms'),
    path('rooms/<int:room_id>/book/', frontend_views.book_room_view, name='book_room'),
    
    # Bookings
    path('my-bookings/', frontend_views.my_bookings_view, name='my_bookings'),
    path('bookings/<int:booking_id>/', frontend_views.booking_detail_view, name='booking_detail'),
    path('bookings/<int:booking_id>/checkin/', frontend_views.checkin_booking_view, name='checkin_booking'),
    path('bookings/<int:booking_id>/checkout/', frontend_views.checkout_booking_view, name='checkout_booking'),
    path('bookings/<int:booking_id>/cancel/', frontend_views.cancel_booking_view, name='cancel_booking'),
]