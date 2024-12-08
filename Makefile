DC = docker compose

# Docker-compose file paths
STORAGES_FILE = docker_compose/storages.yaml
APP_FILE = docker_compose/app.yaml
MONITORING_FILE = docker_compose/monitoring.yaml
TEST_FILE = docker_compose/test.yaml

# Docker-compose container names
APP_CONTAINER = main-app
PROXY_CONTAINER = proxy
DB_CONTAINER = chmnu-db

# Docker commands
EXEC = docker exec
EXEC_IT = docker exec -it
LOGS = docker logs

# Env file path(with docker argument)
ENV = --env-file .env

# Django application specific command
MANAGE_PY = python manage.py

.PHONY: all,
.PHONY: app, app-down, app-logs, # start,end,logs of the main app
.PHONY: proxy-reload, proxy-reload-test, proxy-logs # proxy server commands
.PHONY: storages, storages-logs, storages-down,  # storages(postgres, pgadmin, redis, redisinsight) commands
.PHONY: monitoring, monitoring-logs, monitoring-down, # elastic apm stack commands
.PHONY: postgres, db-logs, # postgres specific commands
.PHONY: migrations, migrate, superuser, loaddata, dumpdata, collectstatic, runscheduler # django manage.py commands

all: app monitoring

app:
		${DC} ${ENV} -f ${APP_FILE} -f ${STORAGES_FILE} up --build -d

app-logs:
		${LOGS} ${APP_CONTAINER} -f

app-down:
		${DC} ${ENV} -f ${APP_FILE} -f ${STORAGES_FILE} -f ${MONITORING_FILE} down

proxy-logs:
		${LOGS} ${PROXY_CONTAINER} -f

proxy-reload:
		${EXEC_IT} ${PROXY_CONTAINER} nginx -s reload

storages:
		${DC} ${ENV} -f ${STORAGES_FILE} up -d

storages-down:
		${DC} -f ${STORAGES_FILE} down

storages-logs:
		${DC} -f ${STORAGES_FILE} logs -f

db-logs:
		${LOGS} ${DB_CONTAINER} -f

postgres:
		@DB_USER=${DB_USER} DB_NAME=${DB_NAME} ${EXEC_IT} ${DB_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME}

monitoring:
	${DC} ${ENV} -f ${MONITORING_FILE} up -d

monitoring-logs:
	${DC} -f ${MONITORING_FILE} ${ENV} logs -f

monitoring-down:
	${DC} -f ${MONITORING_FILE} down

migrate:
		${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} migrate

migrations:
		${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} makemigrations

superuser:
		${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} createsuperuser --no-input

collectstatic:
		${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} collectstatic

dumpdata:
		APP_NAME=${APP_NAME} FILE=${FILE} ${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} dumpdata ${APP_NAME} --indent=4 -o ${FILE}

loaddata:
		APP_NAME=${APP_NAME} ${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} loaddata --app=${APP_NAME} --format=json

run-test:
		${EXEC_IT} ${APP_CONTAINER} pytest -v

runscheduler:
		${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} runscheduler

test-app:
	${DC} ${ENV} -f ${TEST_FILE} up --build -d

test-run-test:
	${EXEC} ${APP_CONTAINER} pytest -v
