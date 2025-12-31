from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/profile/', views.ProfileView.as_view(), name='profile'),
    
    # Booking CRUD endpoints
    path('bookings/', views.BookingListCreateView.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/history/', views.BookingHistoryView.as_view(), name='booking-history'),
    
    # Booking lifecycle endpoints
    path('bookings/<int:pk>/checkin/', views.BookingCheckInView.as_view(), name='booking-checkin'),
    path('bookings/<int:pk>/checkout/', views.BookingCheckOutView.as_view(), name='booking-checkout'),
    path('bookings/<int:pk>/cancel/', views.BookingCancelView.as_view(), name='booking-cancel'),
    
    # Availability check
    path('bookings/check-availability/', views.check_availability, name='check-availability'),
]