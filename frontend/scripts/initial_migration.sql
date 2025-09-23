-- Initial database setup script for poultry management system
-- Run this after setting up your PostgreSQL database

-- Create database (run this as postgres superuser)
-- CREATE DATABASE poultry_management;
-- CREATE USER poultry_user WITH PASSWORD 'your_password_here';
-- GRANT ALL PRIVILEGES ON DATABASE poultry_management TO poultry_user;

-- The following will be handled by Django migrations:
-- python manage.py makemigrations
-- python manage.py migrate

-- Create a superuser account (run this via Django command):
-- python manage.py createsuperuser

-- Optional: Insert some sample data
-- This script can be extended with sample breeds, feed types, etc.
