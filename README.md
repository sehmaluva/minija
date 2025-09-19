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
# MiniJa — Broiler Manager

A small-scale broiler management system (Django backend + React + Vite frontend).
This README focuses on local development setup and recent frontend changes.

## What this repo contains
- Django backend (API): serve at `http://localhost:8000/` in development.
- React frontend (Vite + TypeScript + Tailwind): located under `frontend/frontend` and served at `http://localhost:5173/` in development.

## Quick start (recommended)
Prereqs: Python 3.10+, Node.js 18+, pnpm, PostgreSQL (or SQLite for quick dev), Redis (optional)

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
cd frontend/frontend
pnpm install
pnpm dev
# open http://localhost:5173
```

5. Backend: run server

```bash
python manage.py runserver
# open http://localhost:8000
```

## Frontend notes (recent changes)
- The app uses Vite + React (TypeScript) + TailwindCSS v4 and lucide-react icons.
- App1 (the main SPA) has been restyled to a green "broiler" theme and now exposes pages for:
  - Dashboard
  - Orders
  - Accounting
  - Forecast
  - Reports
  - Settings
- To reduce build-time Tailwind errors we replaced some `@apply` usages with explicit CSS in `src/app1/styles/globals.css`. The app still uses Tailwind utilities, but if you prefer to restore `@apply` usage, inspect `postcss.config.cjs` and `tailwind.config.js` for content globs.

## Backend API highlights
- Authentication endpoints (DRF Token auth):
  - `POST /api/auth/login/` — login, returns `{ user, token }`
  - `POST /api/auth/register/` — user creation
  - `POST /api/auth/logout/`
- Forecast API (simple historical predictor): `/api/forecast/predict/feed/` (see `apps/forecast`)

## Common developer tasks
- Typecheck frontend (from `frontend/frontend`):

```bash
pnpm exec tsc --noEmit
```

- Run Django checks:

```bash
python manage.py check
```

- Create forecast migrations (if you modify models):

```bash
python manage.py makemigrations apps.forecast
python manage.py migrate
```

## Troubleshooting
- Blank frontend or white page:
  - Open developer console in the browser and check for runtime errors (often missing imports or a runtime exception will stop React from rendering).
  - Verify the Vite dev server is running in `frontend/frontend` and that `pnpm dev` prints a local URL.
- Tailwind `@apply` errors:
  - If you see `Cannot apply unknown utility class '...'` when Vite starts, ensure `tailwind.config.js` includes the correct `content` globs (the project includes `src/**/*.{js,ts,jsx,tsx,html,css}`), and `postcss.config.cjs` uses `@tailwindcss/postcss` wrapper.
  - As a quick workaround we converted a few `@apply` uses to plain CSS in `src/app1/styles/globals.css`.
- Login returns HTTP 400 from the client:
  - Check backend logs for the `/api/auth/login/` request and examine the response body — frontend now collapses server validation errors into readable text.

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

---
If you'd like, I can:
- Improve layout spacing on the login page (add consistent gap between inputs and buttons). I already adjusted some input spacing in `src/app1/pages/login/page.tsx` earlier; I can fine-tune it further.
- Create the forecast migrations and seed sample data so the forecast endpoint returns visible predictions.
- Wire orders/accounting pages to backend CRUD endpoints.

Which of those should I do next?
curl -X POST http://localhost:8000/api/auth/register/ \
