import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError


"""
This file defines the core data strctures for each class and represets a database table with the fields.
The models include UserProfile, Listing, Booking, Review
"""

class UserProfile(models.Model):
    """
    THis extends the default django user model profile to include additional fields
    like phone numbers, profile pictures, roles( guest, host, admin)    
    """

    ROLE_CHOICES = [
        ('guest', 'Guest'),   # Reguar user of the application
        ('host', 'Host'),     # User who can create listings
        ('admin', 'Admin'),   # Platform administrator
    ]

    #Primary key using UUID for security purposes
    user_id = models.UUIDField(primary_key =True, default = uuid.uuid4, editable=False, help_text = "Unique Identifier for the user")
    user = models.OneToOneField(User, on_delete = models.CASCADE, help_text = "Link to Django built-in user identification")
    phone_number = models.CharField(max_length = 15, blank = True, null = True, help_text = "Use's phone number")
    profile_picture = models.ImageField(upload_to = 'profile_pics/', blank = True, null = True, help_text = "Use's Profile picture")
    role = models.CharField(max_length = 10, choices = ROLE_CHOICES, default= 'guest', help_text = "User's Role")
    email_verified = models.BooleanField(default = False, help_text = "Whether the user's email has been verified")
    created_at  = models.DateTimeField(auto_now_add = True, help_text = "When the user's profile was created")
    last_login = models.DateTimeField(auto_now_add = True, help_text = 'Last time user logged in')

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

    def get_full_name(self):
        # Retun the user's full name
        return self.user.get_full_name()

    @property
    def is_hot(self):
        # Check if the user is a host
        return self.role == "host"

    @property
    def _is_admin(self):
        return self.role == "admin"

    @property
    def is_guest(self):
        return self.role =="guest"



class Listing(models.Model):
    """
    This models h=shows the property/accommodation that hosts offer

    THis mdoels represents individual propertties (apartments, houses, rooms etc that users can book for their travle)
    """
    # Proprty type choices
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('room', 'Room'),
        ('villa', 'Villa'),
        ('condo', 'Condo'),
        ('townhouse', 'Townhouse'),
        ('cottage','Cottage'),
        ('cabin','Cabin'),
        ('loft', 'Loft'),
        ('other','Other'),
    ]

    # Room type choices 
    ROOM_TYPE_CHOICES = [
        ('entire_place', 'Entire Place'),
        ('private_room', 'Private Room'),
        ('shared_room', 'Shared Room'),
        ('hotel_room', 'Hotel Room'),
    ]

    # Status choices for property approval
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]


    # Primary key using UUID for security purposes
    property_id = models.UUIDField(primary_key = True, default =  uuid.uuid4, help_text = "Unique Identifier for property")
    host = models.ForeignKey(UserProfile, on_delete = models.CASCADE, related_name = 'listings')
    name = models.CharField(max_length = 100, help_text = 'Name of the property')
    description = models.TextField(help_text = "Detailed description of the property")
    property_type = models.CharField(max_length = 50, choices = PROPERTY_TYPE_CHOICES)
    room_type = models.CharField(max_length = 20, choices = ROOM_TYPE_CHOICES, help_text = "Type of room available")


    # Location information
    city = models.CharField(max_length = 100, help_text = "City where the property is located")
    county = models.CharField(max_length = 100, help_text = "County where the property is located")
    postal_code = models.CharField(max_length = 100, help_text = "Postal code of the property")
    # GPS coordinates for mapping
    latitude = models.DecimalField(max_digits =9, decimal_places = 6, help_text = "Location of the property", blank =True, null = True)
    longitude = models.DecimalField(max_digits = 9, help_text = "Longitude location of the property", decimal_places = 8, blank = True, null =True)

    #Property specifications
    bedroom = models.PositiveIntegerField(help_text = "Number of bedrooms")
    bathroom = models.PositiveIntegerField(help_text = "Number of bathrooms")
    max_guests = models.PositiveIntegerField(help_text = "Maximum number of guests allowed")
    # Pricing information
    price_per_night = models.DecimalField(max_digits = 10, decimal_places=2, validators = [MinValueValidator(Decimal('0.01'))], help_text = "Price per night in USD")
    # Status and timestamps
    status = models.CharField(max_length= 220, status = STATUS_CHOICES, default = "pending", help_text = " Approval status of the lsiting")
    created_at = models.DateTimeField(auto_now_add = True, help_text = "When the listing was created")
    updated_at = models.DateTimeField(auto_now_add = True, help_text = "When the listing was updated")


    class Meta:
        db_table = 'listings'
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        ordering = ['-created_at'] # Most recent first
        indexes = [
            models.Index(fields = ['city','county']), #For location-based queries"
            models.Index(fields =['property_type']), #For filtering
            models.Index(fields=['price_per_night']),  # For price sorting
        ]

    def __str__(self):
        return f"{self.name} in {self.city}"
    
    @property
    def is_available(self):
        return self.status =='approved'
    
    @property
    def average_rating(self):
        # Calculate the average rating from reviews
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    @property
    def review_count(self):
        # Get the total number of reviws
        return self.reviews.count()


class Booking(models.Model):
    """
    This is a booking/reservation made by a user
    It basically handles allthe bvooking transations between guests and hosts
    Including dates, pricing, and status tracking
    """

    # Booking status choices
    STATUS_CHOICES = [('pending', 'Pending'),
                      ('confirmed', 'Confirmed'),
                      ('canceled','Cancelled'),
                      ('completed', 'Completed'),
                      ]

    # Primary key using UUID
    booking_id = models.UUIDField(primary_key = True, default = uuid.uuid4,  help_text = " Unique identifier for booking" ,editable = False)
    property = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name = 'bookings', help_text = "The property being booked")
    user = models.ForeignKey(UserProfile, on_delete = models.CASCADE, related_name = 'The guest making the booking')
    start_date = models.DateTimeField(help_text = 'Check in date')
    end_date = models.DateTimeField(help_text = "Check out date")
    # Guests information
    guests = models.PositiveIntegerField(default = 1, validaors = [MinValueValidator(1)], help_text = "Number of guests")
    # Pricing
    total_price = models.DecimalField(max_digits = 10, decimal_places = 2, validators = [MinValueValidator(Decimal('0.00'))])

    # Status and timestamps
    status = models.CharField(max_lengt= 20, choices = STATUS_CHOICES, default = "pending", help_text =  "Current booking status")
    created_at = models.DateTimeField(auto_now_add = True, help_text = " When the booking was created")
    updated_at = models.DateTimeField(auto_now_add  = True, help_text = "When the booking was last updated")

    class Meta:
        db_table = 'bookings'
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ["-created_at"] #  The most recent booking first
        indexes = [
            models.Index(fields = ['start_date', 'end_date']),
            models.Index(fields=['status']),
        ]
        constraints = [
            # Ensure that the end date is after the start date
            models.CheckConstraint(
                check = models.Q(end_date__gt= models.F('start_date')),
                name = 'Valid_date_range'
            ),
        ]
    def __str__(self):
        return f"Bookung {self.booking_id} - {self.property.name}"
    
    @property
    def duration_nights(self):
        return (self.end_date - self.start_date).days
    
    @property
    def is_active(self):
        # Check if the current booking is active
        today = timezone.now().date()
        return (self.status == 'confirmed' and self.start_date  <=today <= self.end_date)        
    
    @property
    def can_be_reviewed(self):
        # Check if the booking can be reviewed( this applies for completed stays only)
        return (self.status == 'completed' and self.end_date < timezone.now().date())
    
    def clean(self):
        # Custom validation to ensure that that booking dates are in the future
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError("End data must always be after the start date")
            
            #Checking if the start date is in the past
            if self.start_date < timezone.now().date():
                raise ValidationError("Start date cannote be in the past")
            
        # check if the guest count does not exceed the property maximum capacity
        if self.guests_count and self.property:
            if self.guests_count > self.property.max_guests:
                raise ValidationError(f" Guest count ({self.guests_count}) exceeds property limit ({self.property.max_guests}) ")


class Review(models.Model):
    """ User review ad rating system
    This model handles the guest reviews for properties after completed stays
    it includes ratings, comments and host responses
    """

    review_id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False,  help_text = " Unique identifier for the review")
    booking = models.OneToOneField(Booking, on_delete = models.CASCADE, related_name = 'review', help_text = "The booking this review is for")
    property = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name = 'reviews' , help_text = "The property being reviewed")
    user = models.ForeignKey(UserProfile, on_delet = models.CASCADE, related_name= 'reviews_written', help_text = "The guest who wrote the review")
    rating = models.PositiveIntegerField(validators = [MinValueValidator(1), MaxValueValidator(5)], help_text = "Rating from 1 to 5 stars")
    comment = models.TextField(blank = True, null=True, help_text = "Optional guest's written review")
    # Responses from the host
    host_response = models.TextField(blank = True, null = True, help_text = "Optional host response")
    host_response_date = models.DateTimeField(blank = True, null = True, help_text = "When the host responded")
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True,help_text = "Whent the review was created")

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields = ['rating']),
            models.Index(fields=['created_at'])
        ]


    def __str__(self):
        return f"Review by {self.user.get_full_name()} - {self.rating} stars"
    
    @property
    def has_host_response(self):
        return bool(self.host_response)
    
    def clean(self):
        """Custom validation to ensure that the review is linked to a completed booking"""
        if self.booking and not self.booking.can_be_reviewed:
            raise ValidationError("Review can only be created only for completed bookings")
        
        if self.booking and self.property:
            if self.booking.property != self.property:
                raise ValidationError("Review property must match the booking property")