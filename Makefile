DC = docker-compose
STORAGES_FILE = docker_compose/storages.yaml
EXEC = docker exec -it
DB_CONTAINER = chmnu-db
LOGS = docker logs
ENV = --env-file .env
DB_USER = myuser
DB_NAME = chmnu_schedule
APP_FILE = docker_compose/app.yaml
APP_CONTAINER = main-app
MANAGE_PY = python manage.py



.PHONY: storages
storages:
		${DC} -f ${STORAGES_FILE} ${ENV} up -d

.PHONY: storages-down
storages-down:
		${DC} -f ${STORAGES_FILE} down

.PHONY: postgres
postgres:
		${EXEC} ${DB_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME}

.PHONY: storages-logs
storages-logs:
		${LOGS} ${DB_CONTAINER} -f

.PHONY: app
app:
		${DC} -f ${APP_FILE} -f ${STORAGES_FILE} ${ENV} up --build -d


.PHONY: app-logs
app-logs:
		${LOGS} ${APP_CONTAINER} -f

.PHONY: app-down
app-down:
		${DC} -f ${APP_FILE} -f ${STORAGES_FILE} down

.PHONY: migrate
migrate:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} migrate

.PHONY: migrations
migrations:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} makemigrations

.PHONY: superuser
superuser:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} createsuperuser --username admin --email admin@admin.com

.PHONY: collectstatic
collectstatic:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} collectstatic


.PHONY: dumpdata
dumpdata:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} dumpdata schedule --indent=4 -o data.json

.PHONY: loaddata
loaddata:
		${EXEC} ${APP_CONTAINER} ${MANAGE_PY} loaddata --app=schedule --format=json

#docker exec -it main-app python manage.py