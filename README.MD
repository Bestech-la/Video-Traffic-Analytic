# Video-Traffic-Analytic-Webapp
the application using refinedjs, nextjs, storybook and tailwindcss
## Webapp

    cd Video-Traffic-Analytic-Webapp

## Install dependency

    npm install

## Run app

    npm run dev

and go url: http://localhost:3000/   

## Run story book

    npm run storybook
and go url: http://localhost:6006/    



# Video-Traffic-Analytic-API

This application enables Django powered websites to have multiple tenants via PostgreSQL schemas. A vital feature for every Software-as-a-Service website.

    # Create a new database
    CREATE DATABASE 'video_traffic_analytic'
## API

To work with the API, navigate to the `Video-Traffic-Analytic-API` directory:

    cd Video-Traffic-Analytic-API

## Basic Settings for Development

Activate environment
    python3 -m venv venv
    source venv/bin/activate

## Install dependencies
    pip install -r dev-requirements.txt


Basic Settings
You’ll have to make the following creations to your your .env file
and Django Secret Key

This revised version specifies that the `.env` file should be created in the `Video-Traffic-Analytic-API` directory,

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


