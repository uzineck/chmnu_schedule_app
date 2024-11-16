from .main import *  # noqa


ALLOWED_HOSTS = ['*']
DEBUG = True
ELASTIC_APM['DEBUG'] = True # noqa
CORS_ALLOWED_ORIGINS = ['http://localhost:3000']
