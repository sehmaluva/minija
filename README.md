# Poultry Management System 

## Features

### Core Functionality

- **User Management**: Role-based authentication (Admin, Manager, Worker, Owner)
-- **Accounting Management**: Keep track of sales and costs.
- **Farm Management**: Multi-farm support with buildings and capacity tracking.
- **Flock Management**: Complete flock lifecycle management with breed tracking.
- **Health Tracking**: Vaccination schedules, medication records, mortality tracking.
- **Production Monitoring**: Feed consumption, egg production, weight tracking, environmental conditions.
- **Reporting & Analytics**: Comprehensive dashboards and custom report generation.
- **Alert System**: Automated alerts for health issues, production anomalies.

#### How to start the app

1. Backend: create & activate virtualenv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

1. Backend: configure env

```bash
touch .env
# edit .env with your database credentials and SECRET_KEY 
```

1. Backend: run migrations and create superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

1. Frontend: install and run

```bash
cd frontend/
pnpm install
pnpm dev
# open http://localhost:3000
```

1. Backend: run server

```bash
python manage.py runserver
# open http://localhost:8000
```

## Common developer tasks

- Typecheck frontend (from `frontend/`):

```bash
pnpm exec tsc --noEmit
```

- Run Django checks:

```bash
python manage.py check
```

## Contributing

Feel free to open an issue or create a PR. Keep changes small and add/update tests when appropriate.
