"""
Django admin configuration for the listings app.

Thus file registers our models to Django admin interface thus 
making it easy to managge data through the admin panel or web interface
"""

from django.contrib import admin
from .models import Listing, Review, Booking, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """ Admin interface for user profiles"""

    list_display = ['user', 'phone_number', 'email_verified', 'created_at']
    list_filter = ['role', 'email_verified', 'created_at']
    search_fields = ['user__username', 'phone_number', 'user__email']
    readonly_fields = ['user_id', 'created_at']     # This are fields that can not ve altered in the admin interface

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """ Admin interface for listings"""

    list_display = ['name','host', 'property_type', 'price_per_night', 'status']
    list_filter = ['status', 'property_type', 'room_type', 'city']
    search_fields = ['name', 'description', 'city']
    readonly_fields = ['property_id ', 'ceated_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'desccription', 'host', 'status')
        }),
        ('Property Details', {
            'fields': ('property_type', 'room_type', 'bedroom', 'bathrooms', 'max_guests')
        }),
        ('Location', {
            'fields': ('city','country', 'postal_code', 'latitude', 'longitude')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )   # THis brings about better organization of fields in the admin, allowing collapsibles and everything


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """ Admin interface for bookings"""
    list_display = ['booking_id', 'property', 'user', 'start_end', 'end_date', 'status', 'total_price']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['property__name', 'user__username']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']
    date_hierarchy = 'start_date'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['review_id', 'property', 'user', 'rating', 'created_at', 'hast_host_response']
    list_filter = ['rating', 'created_at']
    search_fields = ['property__name', 'user__username', 'comment']
    readonly_fields = ['review_id', 'created_at']