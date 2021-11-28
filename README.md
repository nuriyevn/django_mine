https://docs.docker.com/samples/django/

sudo docker-compose run web django-admin startproject composeexample .

docker-compose up --build

django.db.utils.OperationalError: no such table: auth_user
to get rid of

./manage.py migrate

if your Django version is 1.9 or lower, use

./manage.py syncdb

then

python manage.py createsuperuser




