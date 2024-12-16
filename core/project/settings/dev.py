from .main import *  # noqa


ALLOWED_HOSTS = ['*']
DEBUG = True
ELASTIC_APM['DEBUG'] = True # noqa
CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:81']
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://localhost:81']

DJANGO_SUPERUSER_PASSWORD = env('DJANGO_SUPERUSER_PASSWORD') # noqa
DJANGO_SUPERUSER_USERNAME = env('DJANGO_SUPERUSER_USERNAME') # noqa
DJANGO_SUPERUSER_EMAIL = env('DJANGO_SUPERUSER_EMAIL') # noqa
