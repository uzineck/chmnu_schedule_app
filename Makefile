DC = docker-compose

STORAGES_FILE = docker_compose/storages.yaml
APP_FILE = docker_compose/app.yaml
MONITORING_FILE = docker_compose/monitoring.yaml

APP_CONTAINER = main-app

EXEC = docker exec -it
LOGS = docker logs

ENV = --env-file .env

DB_CONTAINER = chmnu-db
DB_USER = myuser
DB_NAME = chmnu_schedule

MANAGE_PY = python manage.py

.PHONY: app, app-logs, app-down, # main app on docker commands
.PHONY: storages, storages-logs, storages-down,  # storages in docker commands
.PHONY: monitoring, monitoring-logs, monitoring-down, # elastic apm in docker commands
.PHONY: postgres, db-logs, # postgres in docker commands
.PHONY: migrations, migrate, superuser, loaddata, dumpdata, collectstatic # django manage.py commands


app:
		${DC} ${ENV} -f ${APP_FILE} -f ${STORAGES_FILE} up --build -d

app-logs:
		${LOGS} ${APP_CONTAINER} -f

app-down:
		${DC} -f ${APP_FILE} -f ${STORAGES_FILE} -f ${MONITORING_FILE} down

storages:
		${DC} -f ${STORAGES_FILE} ${ENV} up -d

storages-down:
		${DC} -f ${STORAGES_FILE} down

storages-logs:
		${LOGS} ${DB_CONTAINER} -f

db-logs:
		${DC} -f ${STORAGES_FILE} logs -f

postgres:
		${EXEC} ${DB_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME}

monitoring:
	${DC} -f ${MONITORING_FILE} ${ENV} up --build -d

monitoring-logs:
	${DC} -f ${MONITORING_FILE} ${ENV} logs -f

monitoring-down:
	${DC} -f ${MONITORING_FILE} down

migrate:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} migrate

migrations:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} makemigrations

superuser:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} createsuperuser --username admin --email admin@admin.com

collectstatic:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} collectstatic

dumpdata:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} dumpdata schedule --indent=4 -o data.json

loaddata:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} loaddata --app=schedule --format=json

#docker exec -it main-app python manage.py