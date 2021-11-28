https://docs.docker.com/samples/django/





django.db.utils.OperationalError: no such table: auth_user
to get rid of

./manage.py migrate

if your Django version is 1.9 or lower, use

./manage.py syncdb

then

python manage.py createsuperuser




