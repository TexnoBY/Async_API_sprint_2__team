#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"


python manage.py migrate --fake --fake movies 0001
python manage.py migrate --no-input


DJANGO_SUPERUSER_USERNAME=admin \
	DJANGO_SUPERUSER_PASSWORD=123123 \
	DJANGO_SUPERUSER_EMAIL=mail@mail.ru \
	python manage.py createsuperuser --noinput || true

gunicorn config.wsgi:application --bind 0.0.0.0:8001 --reload

exec "$@"