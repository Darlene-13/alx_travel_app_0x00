# ALX Travel App

A comprehensive travel booking platform API built with Django REST Framework. This application allows users to list properties, make bookings, and leave reviews - similar to Airbnb.

## Features

- **User Management**: Guest, Host, and Admin roles
- **Property Listings**: Create and manage travel accommodations
- **Booking System**: Make and manage reservations
- **Review System**: Rate and review properties with host responses
- **Advanced Search**: Filter by location, price, dates, and property specs
- **JWT Authentication**: Secure API access
- **Automatic Documentation**: Swagger/OpenAPI integration

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: MySQL
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: Swagger (drf-yasg)
- **Image Processing**: Pillow
- **Background Tasks**: Celery + RabbitMQ

## Quick Start

### Prerequisites

- Python 3.8+
- MySQL
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/alx_travel_app_0x01.git
cd alx_travel_app_0x01
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Create MySQL database**
```sql
CREATE DATABASE alx_travel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Seed database with sample data**
```bash
python manage.py seed --count=20
```

9. **Run the server**
```bash
python manage.py runserver
```

## API Endpoints

### Base URL: `http://localhost:8000/api/v1/`

### Authentication
- `POST /auth/login/` - Login and get JWT token
- `POST /auth/refresh/` - Refresh JWT token

### Users
- `GET /users/` - List all users
- `GET /users/me/` - Get current user profile
- `GET /users/{id}/listings/` - Get user's listings
- `GET /users/{id}/bookings/` - Get user's bookings

### Listings
- `GET /listings/` - List all listings (with filters)
- `POST /listings/` - Create new listing
- `GET /listings/{id}/` - Get listing details
- `GET /listings/{id}/reviews/` - Get listing reviews
- `GET /listings/{id}/availability/` - Check availability
- `GET /listings/search/` - Advanced search

### Bookings
- `GET /bookings/` - List user's bookings
- `POST /bookings/` - Create new booking
- `GET /bookings/{id}/` - Get booking details
- `POST /bookings/{id}/confirm/` - Confirm booking (host only)
- `POST /bookings/{id}/cancel/` - Cancel booking

### Reviews
- `GET /reviews/` - List reviews
- `POST /reviews/` - Create new review
- `GET /reviews/{id}/` - Get review details
- `POST /reviews/{id}/respond/` - Add host response

## Usage Examples

### 1. Get JWT Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### 2. Create a Listing
```bash
curl -X POST http://localhost:8000/api/v1/listings/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cozy Downtown Apartment",
    "description": "Beautiful apartment in the heart of the city",
    "property_type": "apartment",
    "room_type": "entire_place",
    "city": "New York",
    "bedrooms": 2,
    "bathrooms": 1,
    "max_guests": 4,
    "price_per_night": 150.00
  }'
```

### 3. Search Listings
```bash
# Search by city and price range
curl "http://localhost:8000/api/v1/listings/search/?city=New York&min_price=100&max_price=200"

# Filter by property type and guests
curl "http://localhost:8000/api/v1/listings/?property_type=apartment&min_guests=2"
```

### 4. Make a Booking
```bash
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "LISTING_UUID",
    "start_date": "2024-07-01",
    "end_date": "2024-07-07",
    "guests_count": 2
  }'
```

## API Documentation

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Admin Panel**: http://localhost:8000/admin/

## Project Structure

```
alx_travel_app/
├── alx_travel_app/          # Main project settings
│   ├── settings.py          # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py
├── listings/               # Main app
│   ├── models.py           # Database models
│   ├── views.py            # API views and viewsets
│   ├── serializers.py      # API serializers
│   ├── filters.py          # Custom filters
│   ├── admin.py            # Admin configuration
│   ├── urls.py             # App URL patterns
│   └── management/         # Custom management commands
│       └── commands/
│           └── seed.py     # Database seeder
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── manage.py              # Django management script
```

## Testing

### Run Tests
```bash
python manage.py test
```

### Test with Sample Data
```bash
# Clear and reseed database
python manage.py seed --clear --count=50
```

## Environment Variables

Create a `.env` file with:

```env
# Database
DB_NAME=alx_travel_db
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


