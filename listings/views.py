"""
API Views for the listings app.
This file contains Viewswts that provide RESTful API endpoints for:
- LISTING (property management)
- BOOKING (reserversation system)
- REVIEWS (user feedback)
- USERPROFILE  (user management)
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from datetime import date, datetime, timedelta



from .models import UserProfile, Listing, Booking, Review
from .serializers import (
    UserProfileSerializer,
    ListingSerializer,
    BookingSerializer,
    ReviewSerializer
)

from .filters import ListingFilter, BookingFilter

class UserProfileVViews(viewsets.ModelViewSet):
    """
    Viewsets for managing user profiles

    It provides various endpoints for CRUD operations
    -GET /api/v1/users - List all user profiles
    -GET /api/v1/users/{id} - Get specific user profle
    -POST /api/v1/users - Create a new user
    -PUT /api/v1/users/{id} - Update the user profile
    -DELETE /api/v1/users{id} - Delet the user profile
    
    """
    querysey = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'user_id'

    # Filtering and searching
    filter_backend = [DjangoFilterBackend. filters.SearchFilter]
    filterset_fields = ['role', 'email_verifief']
    search_fields = ['user__username', 'user__email', 'user__firstname', 'user__last_name']

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that are required for this views
        """
        if self.action == 'list':
            # Anyone can view the list (for hosts, etc)
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        elif self.action == 'create':
            # ANyone can create the account
            permission_classes = [permissions.AllowAny]
        else:
            # Only authenticated users can view or update their profiles
            permission_clasess = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods = ['get'], permission_classes =[permissions.IsAuthenticated])
    def me(self, request):
        """
        Get the current user's profile
        GET /api/v1/users/me
        """
        try:
            profile = UserProfile.objects.get(user = request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Profile not found'
            }, status= status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods =['get'])
    def listings(self, request, user_id=None):
        """
        
        Get all listings for a specific user (host)
        Get /api/v1/{id}/listings """

        user_profile = self.get_object()
        listings = Listing.objects.filter(host = user_profile)

        # APply pagination if needed
        page = self.paginate_queryset(listings)
        if page is not None:
            serializer = ListingSerializer(page, many =True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ListingSerializer(listings, many =True)
        return Response(serializer.data)
    
    @action (detail = False, methods =['get'])
    def bookings(self, request, user_id = None):
        """
        Get all bookings for a specific user
        Get api/v1/users/{id}/bookings"""

        user_profile = self.get_object()
        bookings = Booking.objects.filter(user=user_profile)

        # Add pagination if needed 
        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = BookingSerializer(page, many = True)
            return self.get_paginated_response(serializer.data)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
class ListingViews(viewsets.ModelViewSet): # This line tells DRF to generate CRUD API endpoints using the listing model
    """
    Viesets for managing property listings
    This provides endpoints for: 
    -GET /api/v1/listings = List all property listings
    -GET /api/v1/listing/{id}/ = Get specific listings 
    -POST /api/v1/listings/ = create a new property listing
    -PUT /api/v1/listings/{id} = update listing
    - DELETE /api/v1/listings/{id} = delet listing

    # Additional endpoints
     - GET /api/v1/listings/{id}/reviews = Get reviews for all listing
     - GET /api/v1/listings/{id}/bookings = Advances search

    """

    serializer_class = ListingSerializer  # Ths lie tells django to use the listing serializer for serializing and deserializing data to and from JSON
    lookup_field = 'property_id'  # Customizes the field used in URLS lookup 

    # Filtering, searching and ordering
    filter_backends = [DjangoFilterBackend, filter.SearchFilter, filter.OrderingFilter]
    filterset_class = ListingFilter # Custom filter class (we'll recreate this)
    search_fields = ['name', 'description', 'city', 'county']
    ordering_fields = ['price_per_night', 'created_at', 'name']
    ordering = ['-created_at'] # Default ordering (newest first)

    def get_queryset(self):   # only return approved listings only
        """
        Customize queryset based on user permissions and filters"""

        if self.action =='list':
            # Base queryset only approved listings for general users
            # For list view, only show approved listings
            return Listing.objects.filter(status = 'approved').select_related('host__user')  #It optimizes the DB queries by joining foreign keys
        else:
            # For detail/create/update/delete, show all listings
            return Listing.objects.all().select_related('host__user')
        

    def get_permissions(self):
        """Set permissions based on actions"""

        if self.action in ['list', 'retrieve']:
            # Anyone can view listings
            permission_classes = [permissions.AllowAny]
        elif self.action =='create':
            # Only authentcated users can create listings
            permission_classes = [permissions.IsAuthenticated]
        else:
            # only listing owners can update or delete
            permission_classess = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):   # This function is called when someone creats a new listing, it ensures that the user has a profile and if not has to create one and it also ensures that they are marked as a host
        """
        Set the host to the current user when creating a listing"""
        # Get or create user profile for the current user
        user_profile, created = UserProfile.objects.get_or_create(
            user = self.request.user,
            defaults = {'role': 'host'}
        )

        # If the user is not a host, update their role
        if user_profile.role != 'host':
            user_profile.role = 'host'
            user_profile.save()

        serializer.save(host = user_profile)
    @action(detail = True, methods=['get'])   # @action decorator is used in viewsets to create custom endpoints that do not follow the standard REST patterns like (list, retrieve, CRUD operations), detail = True means that the route operates on a single object that is listings/{id}/ reviews  and get method means that it will only respond to GET requests only. 
    def reviews(self, request, property_id = None): # Custom endpoint for the listing 
        """
        Get all reviews for a specific listing
        GET /api/v1/listings/{id}/reviews"""

        listing = self.get_object()
        reviews = Review.objects.filter(property=listing).select_related('user__user')

        # Apply pagination if needed
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many = True)
            return self.get_paginated_response(serializer.data)
        serializer = ReviewSerializer(reviews, manay =True)
        return Response(serializer.data)
    
    @action (detail = True, methods=['get'])  # Without the action decorator we would have to create a separate API view or function view
    def availability(self, request, property_id= None):
        """
        Cehck for availabikty for a listing on specific dataes.
        GET /api/v1/listings/{id}/availability? start_date=2024-01-01&end_date=2024
        """
        listing = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date parameters are required.'},
                                status=status.HTTP_400_BAD_REQUEST             
            )
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status = status.HTTP_400_BAD_REQUEST
            )
            

        #Check for conflicting bookings
        conflicting_bookings = Booking.objects.filter(
            property = listing,
            status__in = ['pending', 'confirmed'],
            start_date__lt = end_date,
            end_date__gt = start_date
        )

        is_available = not conflicting_bookings.exists()

        return Response({
            'available': is_available,
            'start_date': start_date,\
            'end_date' : end_date,
            'conflicting_bookings': conflicting_bookings.count()
        })
    @action(detail = False, methods =['get'])
    def search(self, request):
        """ Advanced search for listings
        GET /api/v1/listing/search/?city=NeW yORK& min_price = 100& max_price =300"""

        queryset = self.get_queryset()

        # Location search
        city = request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)

        #  Price range seafch
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        if min_price:
            queryset = queryset.filter(price_per_night__gte = min_price)
        if max_price:
            queryset = queryset. filter(price_per_night__lte = max_price)

        # Property specifications
        bedrooms = request.query_params.get('bedrooms')
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=bedrooms)
        
        guests = request.query_params.get('guests')
        if guests:
            queryset = queryset.filter(max_guests__gte= guests)

        # Apply pagination if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many =True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_srializer(queryset, many =True)
        return Response(serializer.data)
    

class BookingViews(viewsets.ModelViewSet):
    """
    Viewsets for managing bookings
    Its provides the endpoints for:
     -GET /api/v1/bookings/ -Lists the user's bookings
     -GET /api/v1/bookings/{id}/n - Gets the specific booking
     -POST /api/v1/bookings - creates  a new booking
     -PUT /api/v1/bookings/{id}/ - updates the booking
     -DELETE /api/v1/bookings/{id}/ - Cancels the booking"""
    
    serializer_class = BookingSerializer # Tells the viewset to use the Booking serializer for serialzing and deserializing

    lookup_field = 'booking_id'
    permission_classes = [permissions.IsAuthenticated]

    #  Filtering, searching and ordering
    filter_backends = [DjangoFilterBackend, filter.OrderingFilter]
    filterset_class = ListingFilter # custom filyer class (to be created)
    search_fields = ['name', 'description', 'city', 'county']
    ordering_fields = ['price_per_night', 'created_at','name']
    ordering = ['-created_at'] # Default ordering (newest first)

    def get_queryset(self):
        """
        Customize queryset based on user permissions and filters
        """
        if self.action == 'list':
            # For list view only show approved listings
            return Listing.objects.filter(status = 'approved').selected_related('host__user')
        else:
            return Listing.objects.all().select_related('host__user')
        
    def get_permissions(self):
        """ Customize the queryset based on user permissions and filters"""
        if self.action in ['list', 'retrieve']:
            # Anyone can view the bookings
            permission_classes = [permissions.AllowAny]
        elif self.action =='create':
            # Only authenticated users can create bookings'
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
    def perform_create(self, serializer): 
        """
        Set permissions based on actions
        """
        if self.action in ['list', 'retrieve']:
            # Anyone can view the listings
            permission_classes = [permissions.AllowAny]
        elif self.action =='create':
            # only allow authenticated users to create bookings
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAutheticated]
        return [permission() for permission in permission_classes]
    
    def  perform_create(self, serializer):
        """
        Set the host to the current user when creating a listing
        """
        user_profile, created = UserProfile.objects.get_or_create(
            user = self.request.user,
            defaults = {'role': 'host'}
        )

        # If the user is not a host update their role
        if user_profile.role != 'host':
            user_profile.role = 'host'
            user_profile.save()

        serializer.save(host = user_profile)
        
    @action(detail=True, methods = ['get'])
    def reviews(self, request, property_id=None):
        """
        Get all the reviews for a specific listing
        GET /api/v1/listings/{id}/reviews
        """
        listing = self.get_object()
        reviews = Review.objects.filter(property = listing).select_related('user__user')

        # Apply pagination if needed
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many =True)
            return self.get_paginated_response(serializer.data)
        serializer = ReviewSerializer(reviews, many =True)
        return Response(serializer.data)
    
    @action(detail =True, methods=['get'])
    def availability(self, request, property_id = None):
        """
        Check for the availability for a listing on  a specific date
        GET /api/v1/listings/{id}/availability/?start_date=2024-01-01&end_date24-01-07
        """
        listing =  self.get_object()
        start_date = reuest.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date parameters are required'},
                status = status.HTTP_400_BAD_REQUEST
            )
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, status = status.HTTP_400_BAD_REQUEST
            )
        
        # chceck for conflicting bookings
        conflicting_bookings = Booking.objects.filter(
            property= listing,
            status__in = ['pending', 'confirmed'],
            start_date__lt = end_date,
            end_date__gt = start_date
        )

        is_available = not conflicting_bookings.exists()