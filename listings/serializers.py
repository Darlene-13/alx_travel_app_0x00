"""
API serializers for the listing app

These serializers are used to convert between Django models instances and  JSON data.
They hanle data validation, serialization and deserialization for our API
"""

from rest_framework import serializers
from .models import Listing, UserProfile, Review, Booking
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    """ Serializer the userprofile model
    This one handles the extended user information beyond django default user model
    """

    # Include user information for the related user model
    username = serializers.CharField(source = 'user.username', read_only = True)
    email = serializers.EmailField(source = 'user.email', read_only =True)
    first_name = serializers.CharField(source = 'user.first_name', read_only = True)
    last_name = serializers.CharField(source = 'user.last_name', read_only = True)
    class Meta:
        model = UserProfile
        fields = [
            'user_id', 'username', 'email', 
            'first_name', 'last_name', 'phone_number', 'profile_picture',
            'role', 'email_verified', 'created_at'
        ]

        read_only_fields = ['user_id', 'created_at']


class ListingSerializer(serializers.ModelSerializer):
    """ This is a serializer for the property listings model
    It handles the main property data including location, priciing and specifications
    """

    # Include the host information from the UserProfile model
    host = UserProfileSerializer(read_only = True)

    #Calculated fields
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()

    # Display the choices as human-readble texts
    property_type_display = serializers.CharField(source = 'get_property_type_display', read_only = True)
    room_type_display = serializers.CharField(source = 'get_room_type_display', read_only =True)
    status_display = serializers.CharField(source = 'get_status_display', read_only =True)

    class Meta:
        model = Listing
        fields = [
             'property_id', 'host', 'name', 'description',
             'property_type', 'room_type', 'property_type_display', 'room_type_display',
             'city', 'county', 'postal_code', 'latitude', 'longitude',
             'bedrooms', 'bathrooms', 'max_guests', 'price_per_night',
             'status', 'status_display', 'created_at', 'updated_at', 'is_available',
             'average_rating', 'review_count'

        ]
        read_only_fields = ['property_id', 'created_id', 'updated_at']

    def validate_price_per_night(self, value):
        """ Custom validation for price_per_night_field"""
        if value <= 0:
            raise serializers.ValidationError("Price per_night must be greater than 0")
        return value
    
    def validat(self, data):
        if data.get('bedroom', 0) < 0:
            raise serializers.ValidationError("Bedrooms cannot be negative")
        if  data.get('bathrooms', 0)  < 0:
            raise serializers.ValidationError('Bathrooms cannote be negative')
        if data.get('max_guests', 0) <= 0:
            raise serializers.ValidationError("Max guests must be atleast 3")
        return data
    
class BookingSerializer(serializers.ModelSerializer):
    """ Serializer for the booking model
    This handles the booking data including user, property and , dates, pricing, status"""

    # Include the related model data
    property = ListingSerializer(read_only =True)
    user = UserProfileSerializer(read_only =True)

    # For creating bookings (write only fields)
    property_id = serializers.UUIDField(write_only = True)
    user_id = serializers.UUIDField(write_only =True)

    # Calculated fields
    duration_nights = serializers.ReadOnlyField()
    is_actieve = serializers.ReadOnlyField()
    can_be_reviewed = serializers.ReadOnlyField()

    # Display the status as human-readble test
    status = serializers.CharField(source = 'get_status_display')

    class Meta:
        fields = [
            'booking_id', 'property', 'user', 'property_id', 'user_id',
            'start_date', 'end_date', 'guests_count', 'total_price',
            'status', 'status_display', 'duration_nights', 'is_active', 'can_be_reviewed',
            'created_at', 'updated_at'
        ]

        read_only_fields = ['booking_id', 'created_at', 'updated_at']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError("End date must be after the start date")
            
            #Validate the guest count against propery limits
            property_id = data.get('property_id')
            guests_count = data.get('guests_count')

            if property_id and guests_count:
                try:
                    listing = Listing.objects.get(property_id=property_id)
                    if guests_count > listing.max_guests:
                        raise serializers.ValidationError(
                            f" Guests count ({guests_count}) cannot exceed property limit ({listing.max_guests})")
                except Listing.DoesNotExist:
                    raise serializers.ValidationError("Invalid property_id")
                
            return data
        


    def create(self, validated_data):
        #Custom create method to handle foreign key relationships
        property_id = validated_data.pop('property_id')
        user_id = validated_data.pop('user_id')

        try:
            property_obj = Listing.objects.get(property_id=property_id)
            user_obj = UserProfile.objects.get(user_id = user_id)
        except (Listing.DoesNotExist, UserProfile.DoesNotExist):
            raise serializers.ValidationError("Invalid property or user ID")
        
        #create the booking
        booking = Booking.objects.create(

            property = property_obj,
            user = user_obj,
            **validated_data
        )
        return booking
    

class ReviewSerializer(serializers.ModelSerializer):
    """ Serializer for review data.
    This handles the user reviews and ratings for properties
    """

    #Include related model data
    user = UserProfileSerializer(read_only =True)
    property = ListingSerializer(read_only = True)

    # For creating reviews (write-only fields)
    booking_id = serializers.UUIDField(write_only = True)
    property_id = serializers.UUIDField(write_only =True)
    user_id = serializers.UUIDField(write_only =True)


    #  Calculated fields
    has_host_response = serializers.ReadOnly()

    class Meta:
        model = Review 
        fields = [
            'review_id', 'booking_id', 'property', 'user', 'property_id', 'user_id',
            'rating', 'comment', 'host_response', 'host_response_date',
            'has_host_response', 'created_at'
        ]

        read_only_fields = ['review_id', 'created_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def create(self, validated_data):
        """ Custom method to handle foreign key relationships"""
        # Extract the IDs
        booking_id = validated_data.pop('booking_id')
        property_id = validated_data.pop('property_id')
        user_id = validated_data.pop('user_id')

        #Get the actual objects
        try:
            booking_obj = Booking.objects.get(booking_id = booking_id)
            property_obj = Listing.object.get(property_id = property_id)
            user_obj = UserProfile.objects.get(user_id = user_id)

        except (Booking.DoesNotExist, Listing.DoesNotExist, UserProfile.DoesNotExist):
            raise serializers.ValidationError("Invalid booking, property or user Id")
        
        #Validate that booking is completed and can be reviewed
        if not booking_obj.can_be_reviewed:
            raise serializers.ValidationError("Can only review completed bookings")
        
        # create the review
        review = Review.objects.create(
            booking = booking_obj,
            property = property_obj,
            user = user_obj,
            **validated_data
        )

        return review