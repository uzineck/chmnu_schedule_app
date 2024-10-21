#!/bin/bash

# python manage.py runserver 0.0.0.0:8000
gunicorn core.project.wsgi:application -w 8 --bind 0.0.0.0:8000 --reload
