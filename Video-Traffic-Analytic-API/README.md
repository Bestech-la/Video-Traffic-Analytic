# Video-Traffic-Analytic-API

This application enables Django powered websites to have multiple tenants via PostgreSQL schemas. A vital feature for every Software-as-a-Service website.

    # Create a new database
    CREATE DATABASE 'video_traffic_analytic'

## Basic Settings for Development

Activate environment

    python3 -m venv venv
    source venv/bin/activate

## Install dependencies
    pip install -r dev-requirements.txt


Basic Settings
You’ll have to make the following creations to your your .env file
and Django Secret Key

    DB_NAME=your_database_name
    DB_USR=your_user_name
    DB_PWD=your_password

    SECRET_KEY='your_secret_key'
    JWT_SECRET_KEY='your_jwt_secret_key'

## Make migrations and Apply to database # create migrations files (every new django app)

    python manage.py makemigrations
    python manage.py makemigrations video infraction_tracker
    python manage.py migrate

## Setup Initial User, and Admin

    # create first user
    python manage.py createsuperuser
    python manage.py runserver

## Go to
    localhost:8000/admin/ or localhost:8000/swagger/


## Create a new model
    cd apps
    python ../manage.py startapp "folder name"
