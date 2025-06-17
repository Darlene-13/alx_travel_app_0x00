


"""
URL patterns for the listings app API endpoints.

This file configures all the REST API endpoints using DRF routers.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    UserProfileViewSet,
    ListingViewSet,
    BookingViewSet,
    ReviewViewSet
)

# Create a router and register our viewsets
router = DefaultRouter()

# Register viewsets with the router
# This automatically creates all CRUD endpoints
router.register(r'users', UserProfileViewSet, basename='userprofile')
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')

# URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

app_name = 'listings'