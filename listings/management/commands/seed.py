"""
The management command to seed the database with some sample data

THis command created sample listings, users, bookings, and reviews for testing and development purposes

Usage: Python manage.py seed
"""



from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random
from datetime import date



from listings.models import UserProfile, Listing, Booking,Review

class Command(BaseCommand):
    help = 'Seed the database with sample travel listings data'

    def add_arguments(self, parser):
        #Add command line arguments
        parser.add_argument(
            '--clear',
            action = 'store_true',
            help = 'Clear existing data before seeding',
        )

        parser.add_argument(
            '--count',
            type = int,
            default = 20,
            help = 'Number of listings to create (default: 20)'
        )

    def handle(self, *args, **options):
        """ Handle the main command"""
        self.stdout.write(
            self.style.SUCCESS('Starting database seeding...')

        )

        if options['clear']:
            self.clear_data()

            self.create_users()
            self.create_listings(options['count'])
            self.create_bookings()
            self.create_reviews()

            self.stdout.write(
                self.style.SUCCESS('Databse seeding completed successfully!')

            )


    def create_users(self):
        """Create sample users and profiles"""
        self.stdout.write('Creating sample users...')
        
        # Sample user data
        users_data = [
            {
                'username': 'john_host',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'host',
                'phone': '+1-555-0101'
            },
            {
                'username': 'sarah_host',
                'email': 'sarah@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'host',
                'phone': '+1-555-0102'
            },
            {
                'username': 'mike_guest',
                'email': 'mike@example.com',
                'first_name': 'Mike',
                'last_name': 'Brown',
                'role': 'guest',
                'phone': '+1-555-0201'
            },
            {
                'username': 'emily_guest',
                'email': 'emily@example.com',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'role': 'guest',
                'phone': '+1-555-0202'
            },
            {
                'username': 'admin_user',
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'phone': '+1-555-0001'
            }
        ]

        for user_data in users_data:
            # Create Django User instance
            user = User.objects.create_user(
                username = user_data['username'],
                email = user_data['email'],
                password = "testpass123",
                first_name = user_data['first_name'],
                last_name = user_data['last_name']
            )

            # Create user profile
            UserProfile.objects.create(
                user = user,
                phone_number = user_data['phone'],
                role = user_data['role'],
                email_verified = True if user_data['role'] == 'admin' else False
            )
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(users_data)} users")
        )
        

    def create_listings(self, count):
        """ Create sammple property listings"""
        self.std.write(f"Creating {count} sample listings ....")

        # GET HOST USERS
        hosts = UserProfile.objects.filter(role = 'host')

        #Sample listting data
        property_types = ['apartment', 'house', 'cottage', 'villa', 'condo', 'cabin']
        room_types = ['entire_place', 'private_room', 'shared_room']
        cities = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
            'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose',
            'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'San Francisco'
        ]

        # Sample property names
        property_names = [
            'Cozy Apartment', 'Luxury Villa', 'Charming Cottage', 'Modern Condo',
            'Spacious House', 'Rustic Cabin', 'Stylish Loft', 'Beachfront Bungalow',
            'Downtown Studio', 'Countryside Retreat'
        ]

        for i in range(count):
            host = random.choice(hosts)
            listing = Listing.objects.create(
                host = host,
                name = f"{random.choice(property_names)} {i+1}",
                description = f"Beautiful {random.choice(property_types)} in {random.choice(cities)}"
                              f" Perfect for travellers seeking comfort and convinence"
                            f" THis property offers modern amenities and a great location",

            property_type = random.choice(property_types),
            room_type = random.choice(room_types),
            city = random.choice(cities),
            county = f" {random.choice(['county', 'District', 'Region'])} {i + 1}",
            latitude = Decimal (str(round(random.uniform(25.0, 50.0), 6))),
            longitude = Decimal(str(round(random.uniform(-125.0, -70.0), 6))),
            bedrooms = random.randint(1,5),
            bathrooms = random.randint(1,3),
            max_guests = random.randint(1,8),
            price_per_night = Decimal(str(random.randint(2000, 20000))),
            status = 'approved',
            )
        self.stdout.write(
            self.style.SUCCESS(F"Created  {count} listings")
        )
    def create_bookings(self):
        """Create sample bookings"""
        self.stdout.write("Creating sample bookings")

        # Get the guests and listings
        guests = UserProfile.objects.filter(role = 'guest')
        listings = Listing.objects.filter(status = "approved")

        booking_count = 0

        for _ in range(30):
            guest = random.choice(guests)
            listing = random.choice(listings)

            # Generate the random dates
            start_date = date.today() + timedelta(days = random.randint(-30, 60))
            duration = random.randint(1,14)
            end_date = start_date + timedelta(days = duration)

            # Calculate the total price
            total_price = listing.price_per_night * duration

            # Random status based on the date
            if end_date < date.today():
                status = random.choice(['completed', 'cancelled'])
            elif start_date <= date.today():
                status = 'confirmed'
            else:
                status = random.choice(['pending', 'confirmed'])


            booking = Booking.objects.create(
                property = listing,
                user = guest,
                start_date = start_date,
                guests_count = random.randint(1, min(listing.max_guests, 4)),
                total_price = total_price,
                status = status
            )

            booking_count += 1

        self.stdout.write(
            self.style.SUCCESS (f" Created {booking_count} bookings")
        )

    def create_reviews(self):
        """ Create sample reviews for completed bookings"""
        self.stdout.write("Creating sample reviews")

        #Get completed bookinggs that can be reviewed
        completed_bookings = Booking.objects.filter(
            status = 'completed',
            end_date__lt = date.today()
        )

        # Sample reviw comments 
        positive_comments = [
            "Amazing stay! Highly recommend this place.",
            "The host was very welcoming and the property was exactly as described.",
            "Great location and very comfortable. Would definitely book again!",
            "Had a wonderful time, the amenities were top-notch.",
            "Perfect for a weekend getaway, everything was clean and well-maintained."
        ]
        negative_comments = [
            "The place was not as described, very disappointed.",
            "Had issues with cleanliness, would not recommend.",
            "The host was unresponsive and the check-in process was a hassle.",
            "Not worth the price, expected better quality.",
            "Location was noisy and not as convenient as advertised."
        ]

        review_count = 0


        # Create reviews for about 70 % of completed bookings
        for booking in completed_bookings:
            if random.random() < 0.7:
                rating = random.randint(1,5)

                if rating >=4:
                    comment = random.choice(positive_comments)
                else:
                    comment = random.choice(negative_comments)

                review = Review.objects.create(
                    booking = booking,
                    user = booking.user,
                    property = booking.property,
                    rating = rating,
                    comment = comment
                )

                #Add host responses for some reviews
                if random.random() < 0.6:
                    review.host_response = "Thank you for your review! We are glad you enjoyed your stay."
                    review.host_response_date = timezone.now()
                    review.save()

                review_count += 1
            self.stdout.write(
                self.style.SUCCESS(f"Created {review_count} reviews")
            )