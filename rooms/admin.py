from django.contrib import admin
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """
    Admin interface for Room model
    """
    list_display = [
        'room_number', 'room_type', 'capacity', 
        'hourly_rate', 'daily_rate', 'status', 'floor'
    ]
    list_filter = ['room_type', 'status', 'floor', 'capacity']
    search_fields = ['room_number', 'description']
    ordering = ['room_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('room_number', 'room_type', 'capacity', 'floor', 'status')
        }),
        ('Pricing', {
            'fields': ('hourly_rate', 'daily_rate')
        }),
        ('Details', {
            'fields': ('description', 'amenities', 'image_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    list_per_page = 25
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related()