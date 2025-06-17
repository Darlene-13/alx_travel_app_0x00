"""
Custom filter classes for advanced filtering capabilities.

These filters provide advanced search and filtering options for our API endpoints.
"""

import django_filters
from django_filters import rest_framework as filters
from .models import Listing, Booking


class ListingFilter(filters.FilterSet):
    """
    Advanced filtering for listings.
    
    Provides filters for:
    - Price range
    - Property specifications
    - Location
    - Availability dates
    """
    
    # Price range filters
    min_price = filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')
    
    # Property specification filters
    min_bedrooms = filters.NumberFilter(field_name='bedrooms', lookup_expr='gte')
    min_bathrooms = filters.NumberFilter(field_name='bathrooms', lookup_expr='gte')
    min_guests = filters.NumberFilter(field_name='max_guests', lookup_expr='gte')
    
    # Location filters
    city = filters.CharFilter(field_name='city', lookup_expr='icontains')
    county = filters.CharFilter(field_name='county', lookup_expr='icontains')
    
    # Property type filters
    property_type = filters.MultipleChoiceFilter(
        choices=Listing.PROPERTY_TYPE_CHOICES,
        field_name='property_type'
    )
    
    room_type = filters.MultipleChoiceFilter(
        choices=Listing.ROOM_TYPE_CHOICES,
        field_name='room_type'
    )
    
    # Date availability filter (custom method)
    available_from = filters.DateFilter(method='filter_available_from')
    available_to = filters.DateFilter(method='filter_available_to')
    
    class Meta:
        model = Listing
        fields = [
            'property_type', 'room_type', 'status',
            'min_price', 'max_price', 
            'min_bedrooms', 'min_bathrooms', 'min_guests',
            'city', 'county'
        ]
    
    def filter_available_from(self, queryset, name, value):
        """
        Filter listings available from a specific date.
        """
        # Exclude listings with confirmed bookings that overlap with the requested period
        from django.db.models import Q
        
        if value:
            # Find listings with conflicting bookings
            conflicting_bookings = Booking.objects.filter(
                status__in=['pending', 'confirmed'],
                start_date__lte=value,
                end_date__gt=value
            ).values_list('property_id', flat=True)
            
            # Exclude listings with conflicting bookings
            queryset = queryset.exclude(property_id__in=conflicting_bookings)
        
        return queryset
    
    def filter_available_to(self, queryset, name, value):
        """
        Filter listings available until a specific date.
        """
        from django.db.models import Q
        
        if value:
            # Find listings with conflicting bookings
            conflicting_bookings = Booking.objects.filter(
                status__in=['pending', 'confirmed'],
                start_date__lt=value,
                end_date__gte=value
            ).values_list('property_id', flat=True)
            
            # Exclude listings with conflicting bookings
            queryset = queryset.exclude(property_id__in=conflicting_bookings)
        
        return queryset


class BookingFilter(filters.FilterSet):
    """
    Advanced filtering for bookings.
    """
    
    # Date range filters
    start_date_from = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_from = filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = filters.DateFilter(field_name='end_date', lookup_expr='lte')
    
    # Price range filters
    min_price = filters.NumberFilter(field_name='total_price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='total_price', lookup_expr='lte')
    
    # Property filters
    property_city = filters.CharFilter(field_name='property__city', lookup_expr='icontains')
    property_type = filters.CharFilter(field_name='property__property_type')
    
    class Meta:
        model = Booking
        fields = [
            'status', 'guests_count',
            'start_date_from', 'start_date_to',
            'end_date_from', 'end_date_to',
            'min_price', 'max_price',
            'property_city', 'property_type'
        ]