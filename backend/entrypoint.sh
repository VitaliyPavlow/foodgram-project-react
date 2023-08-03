#!/bin/bash

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py import_csv Ingredient data/ingredients.csv
python manage.py import_csv Tag data/tags.csv
gunicorn --bind 0.0.0.0:8000 foodgram_backend.wsgi
