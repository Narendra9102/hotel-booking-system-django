from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    # Room listing and details
    path('rooms/', views.RoomListView.as_view(), name='room-list'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room-detail'),
    
    # Room search and availability
    path('rooms/search-available/', views.search_available_rooms, name='search-available'),
    path('rooms/types/', views.room_types, name='room-types'),
]