This folder contains Docker support for the project.

Quick start (example):

1. Copy or create a `.env` file at project root with DB credentials and Django secret:

   DB_NAME=poultry1
   DB_USER=seh
   DB_PASSWORD=yourpassword
   DB_HOST=db
   DB_PORT=5432
   SECRET_KEY=changeme
   DEBUG=True

2. Build and start the stack:

   docker compose up --build

The `frontend-build` service will run `pnpm install` and `pnpm run build` into `frontend/frontend/dist` and the `nginx` service serves those static files and proxies `/api/` to the `django` service.

Notes:
- Ensure `docker/django/entrypoint.sh` is executable (chmod +x docker/django/entrypoint.sh)
- You may need to install pnpm on the frontend build image or adjust node versions.
