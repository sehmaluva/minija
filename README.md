# Minija Poultry Management App

## Project Purpose

Minija is a poultry management platform built to help farmers and poultry businesses run daily operations, track performance, and make better business decisions from one system.

## Main Goals

- Improve day-to-day farm operations with accurate record keeping.
- Give clear visibility into production, health, finance, and orders.
- Reduce manual paperwork and improve data consistency.
- Support organization-based access for teams and farm staff.
- Provide timely insights through reports and forecasting.

## Core Features

### 1. Bird and Batch Management

- Create and manage poultry batches.
- Track bird lifecycle details and status.
- Organize records by farm/organization.

### 2. Production Tracking

- Capture daily production metrics.
- Monitor trends over time for operational decisions.
- Support production performance analysis.

### 3. Health Monitoring

- Record health events, treatments, and interventions.
- Maintain traceable health history by batch.
- Improve early response to disease and mortality risks.

### 4. Accounting and Cost Control

- Log poultry-related income and expenses.
- Track operational costs and profitability.
- Support financial visibility per organization.

### 5. Orders and Sales Flow

- Manage customer orders.
- Track order lifecycle and fulfillment.
- Connect operations to revenue tracking.

### 6. Forecasting and Reporting

- Generate reports for operations and finance.
- Forecast trends to support planning.
- Provide management insights for better decisions.

### 7. Authentication and Access Control

- JWT-based authentication.
- Role and permission-aware access.
- Organization context for multi-tenant data isolation.

## Technology Stack

- Backend: Django + Django REST Framework
- Database: PostgreSQL
- Authentication: SimpleJWT
- Async tasks: Celery + Redis
- API documentation: drf-spectacular (OpenAPI/Swagger)
- Frontend: Next.js
- Containerization: Docker/Podman compatible setup

## Who This Project Is For

- Poultry farm owners and managers
- Farm operations teams
- Poultry businesses that need production and financial visibility

## Vision

Build a reliable, production-ready poultry management system that combines farm operations, financial performance, and decision support in one platform.
