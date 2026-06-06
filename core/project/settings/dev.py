from .main import *  # noqa


ALLOWED_HOSTS = ['*']
DEBUG = True
CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:81']
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://localhost:81']

REFRESH_COOKIE_SECURE = False
