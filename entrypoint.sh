#!/bin/bash
# !WARNING This file should not contain last blank line
WORKERS="${GUNICORN_WORKERS:-2}"
if [ "${DJANGO_ENV}" = "dev" ]; then
    exec gunicorn core.project.wsgi:application -w "${WORKERS}" --bind 0.0.0.0:8000 --reload
else
    exec gunicorn core.project.wsgi:application -w "${WORKERS}" --bind 0.0.0.0:8000
fi