#!/bin/bash

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
cp -r collected_static/* backend_static/
gunicorn --bind 0.0.0.0:8000 foodgram_backend.wsgi
