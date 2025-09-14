# Poultry Management System Backend

A comprehensive Django REST API backend for managing poultry farms, flocks, health records, production data, and analytics.

## Features

### Core Functionality
- **User Management**: Role-based authentication (Admin, Manager, Worker, Veterinarian, Owner)
- **Farm Management**: Multi-farm support with buildings and capacity tracking
- **Flock Management**: Complete flock lifecycle management with breed tracking
- **Health Tracking**: Vaccination schedules, medication records, mortality tracking
- **Production Monitoring**: Feed consumption, egg production, weight tracking, environmental conditions
- **Reporting & Analytics**: Comprehensive dashboards and custom report generation
- **Alert System**: Automated alerts for health issues, production anomalies

### API Endpoints

#### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `POST /api/auth/change-password/` - Change password

#### Farm Management
- `GET /api/farms/` - List farms
- `POST /api/farms/` - Create farm
- `GET /api/farms/{id}/` - Get farm details
- `GET /api/farms/summary/` - Farm statistics
- `GET /api/farms/buildings/` - List buildings

#### Flock Management
- `GET /api/flocks/` - List flocks
- `POST /api/flocks/` - Create flock
- `GET /api/flocks/{id}/` - Get flock details
- `GET /api/flocks/statistics/` - Flock statistics
- `GET /api/flocks/breeds/` - List breeds
- `GET /api/flocks/movements/` - Flock movements

#### Health Tracking
- `GET /api/health/records/` - Health records
- `POST /api/health/records/` - Create health record
- `GET /api/health/mortality/` - Mortality records
- `GET /api/health/dashboard/` - Health dashboard

#### Production Monitoring
- `GET /api/production/feed/` - Feed consumption records
- `GET /api/production/eggs/` - Egg production records
- `GET /api/production/weights/` - Weight tracking records
- `GET /api/production/environmental/` - Environmental conditions
- `GET /api/production/dashboard/` - Production dashboard

#### Reports & Analytics
- `GET /api/reports/` - List reports
- `POST /api/reports/generate/` - Generate custom report
- `GET /api/reports/analytics/dashboard/` - Analytics dashboard
- `GET /api/reports/alerts/` - System alerts

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (for Celery tasks)

### Setup

1. **Clone the repository**
\`\`\`bash
git clone <repository-url>
cd poultry-management-backend
\`\`\`

2. **Create virtual environment**
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. **Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Environment Configuration**
\`\`\`bash
cp .env.example .env
# Edit .env with your database and other settings
\`\`\`

5. **Database Setup**
\`\`\`bash
# Create PostgreSQL database
createdb poultry_db

# Run migrations
python manage.py makemigrations
python manage.py migrate
\`\`\`

6. **Create Superuser**
\`\`\`bash
python manage.py createsuperuser
\`\`\`

7. **Seed Initial Data** (Optional)
\`\`\`bash
python scripts/seed_initial_data.py
\`\`\`

8. **Run Development Server**
\`\`\`bash
python manage.py runserver
\`\`\`

The API will be available at `http://localhost:8000/`

### API Documentation
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

## Configuration

### Environment Variables
\`\`\`env
# Database
DB_NAME=your_database_name
DB_USER=your_database_use
DB_PASSWORD=your_database_password
DB_HOST=your_database_host_address
DB_PORT=your_database_host.port

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0
\`\`\`

### User Roles & Permissions

- **Admin**: Full system access
- **Owner**: Manage owned farms and all related data
- **Manager**: Manage assigned farms and flocks
- **Veterinarian**: Access health records and create treatments
- **Worker**: Basic production data entry

## API Usage Examples

### Authentication
\`\`\`bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user123",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "manager"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
\`\`\`

### Create Farm
\`\`\`bash
curl -X POST http://localhost:8000/api/farms/ \
  -H "Authorization: Token your-auth-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Green Valley Farm",
    "address": "123 Farm Road",
    "city": "Farmville",
    "state": "Iowa",
    "country": "USA",
    "license_number": "PF-2024-002",
    "established_date": "2024-01-01",
    "total_area": 25.5
  }'
\`\`\`

### Record Egg Production
\`\`\`bash
curl -X POST http://localhost:8000/api/production/eggs/ \
  -H "Authorization: Token your-auth-token" \
  -H "Content-Type: application/json" \
  -d '{
    "flock": 1,
    "date": "2024-01-15",
    "total_eggs": 4200,
    "grade_a_eggs": 3800,
    "grade_b_eggs": 300,
    "grade_c_eggs": 80,
    "cracked_eggs": 15,
    "dirty_eggs": 5,
    "average_weight": 63.2
  }'
\`\`\`

## Development

### Running Tests
\`\`\`bash
python manage.py test
\`\`\`

### Code Quality
\`\`\`bash
# Format code
black .

# Lint code  
flake8 .
\`\`\`

### Background Tasks
Start Celery worker for background tasks:
\`\`\`bash
celery -A core worker -l info
\`\`\`

## Production Deployment

### Using Docker
\`\`\`bash
# Build image
docker build -t poultry-backend .

# Run container
docker run -p 8000:8000 --env-file .env poultry-backend
\`\`\`

### Using Gunicorn
\`\`\`bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000
\`\`\`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team.
