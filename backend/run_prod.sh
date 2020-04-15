#!/bin/sh
export DJANGO_SETTINGS=prod
cd /app
python3 manage.py migrate
python3 manage.py loaddata demodata.yaml
uwsgi --ini /app/config/uwsgi-prod.ini
