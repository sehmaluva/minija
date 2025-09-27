# Poultry Management System 
## Features

### Core Functionality
- **User Management**: Role-based authentication (Admin, Manager, Worker, Owner)
- **Farm Management**: Multi-farm support with buildings and capacity tracking
- **Flock Management**: Complete flock lifecycle management with breed tracking
- **Health Tracking**: Vaccination schedules, medication records, mortality tracking
- **Production Monitoring**: Feed consumption, egg production, weight tracking, environmental conditions
- **Reporting & Analytics**: Comprehensive dashboards and custom report generation
- **Alert System**: Automated alerts for health issues, production anomalies

1. Backend: create & activate virtualenv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Backend: configure env

```bash
cp .env.example .env
# edit .env with your database credentials and SECRET_KEY
```

3. Backend: run migrations and create superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

4. Frontend: install and run

```bash
cd frontend/
pnpm install
pnpm dev
# open http://localhost:5173
```

5. Backend: run server

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

## Deployment hints
- Production build (frontend):

```bash
cd frontend/frontend
pnpm build
# serve `dist` with nginx or embed in Docker image
```

- Docker: see `docker/` and `docker-compose.yml` in repo for example compose that reverse-proxies the SPA and proxies `/api` to Django.

## Contributing
Open an issue or create a PR. Keep changes small and add/update tests when appropriate.


