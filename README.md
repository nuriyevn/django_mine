https://docs.docker.com/samples/django/

sudo docker-compose run web django-admin startproject djangomine .

docker-compose up --build

django.db.utils.OperationalError: no such table: auth_user
to get rid of

./manage.py migrate

if your Django version is 1.9 or lower, use

./manage.py syncdb

then

python manage.py createsuperuser
admin:C....4...



tutorial:

https://docs.djangoproject.com/en/3.2/intro/tutorial02/
tutorial 2:
https://www.enterprisedb.com/postgres-tutorials/how-use-postgresql-django


Create user:


CREATE DATABASE minebase;
CREATE USER mineuser WITH PASSWORD '.8.2.';
ALTER ROLE mineuser SET client_encoding TO 'utf8'; 
ALTER ROLE mineuser SET default_transaction_isolation TO 'read committed'; 
ALTER ROLE mineuser SET timezone TO 'Europe/Helsinki';

GRANT ALL PRIVILEGES ON DATABASE minebase TO mineuser;
\q


