DC = docker compose

# Docker-compose file paths
STORAGES_FILE = docker_compose/storages.yaml
APP_FILE = docker_compose/app.yaml
APP_PROD_FILE = docker_compose/app.prod.yaml
MONITORING_FILE = docker_compose/monitoring.yaml
TEST_FILE = docker_compose/test.yaml

# Docker-compose container names
APP_CONTAINER = main-app
PROXY_CONTAINER = proxy
DB_CONTAINER = chmnu-db
CACHE_CONTAINER = chmnu-db-cache

# Docker commands
EXEC = docker exec
EXEC_IT = docker exec -it
LOGS = docker logs

# Env file path (with docker argument)
ENV = --env-file .env

# Django application specific command
MANAGE_PY = python manage.py

.PHONY: all
.PHONY: app app-down app-logs
.PHONY: app-prod app-prod-down
.PHONY: storages storages-down storages-logs
.PHONY: proxy-logs proxy-reload
.PHONY: monitoring monitoring-logs monitoring-down
.PHONY: db-logs postgres cache-flush
.PHONY: migrations migrate superuser loaddata dumpdata collectstatic runscheduler
.PHONY: test-app test-down test-restart test-run test-migrate

all: app monitoring

# --- App ---

app:
	${DC} ${ENV} --profile dev -f ${APP_FILE} -f ${STORAGES_FILE} up --build -d

app-logs:
	${LOGS} ${APP_CONTAINER} -f

app-down:
	${DC} ${ENV} --profile dev -f ${APP_FILE} -f ${STORAGES_FILE} down

# --- App (prod) ---

app-prod:
	${DC} ${ENV} -f ${APP_PROD_FILE} -f ${STORAGES_FILE} up --build -d

app-prod-down:
	${DC} ${ENV} -f ${APP_PROD_FILE} -f ${STORAGES_FILE} down

# --- Storages ---

storages:
	${DC} ${ENV} --profile dev -f ${STORAGES_FILE} up -d

storages-down:
	${DC} ${ENV} --profile dev -f ${STORAGES_FILE} down

storages-logs:
	${DC} ${ENV} -f ${STORAGES_FILE} logs -f

db-logs:
	${LOGS} ${DB_CONTAINER} -f

postgres:
	${EXEC_IT} ${DB_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME}

cache-flush:
	${EXEC} ${CACHE_CONTAINER} redis-cli FLUSHDB

# --- Proxy ---

proxy-logs:
	${LOGS} ${PROXY_CONTAINER} -f

proxy-reload:
	${EXEC_IT} ${PROXY_CONTAINER} nginx -s reload

# --- Monitoring ---

monitoring:
	${DC} ${ENV} -f ${MONITORING_FILE} up -d

monitoring-logs:
	${DC} ${ENV} -f ${MONITORING_FILE} logs -f

monitoring-down:
	${DC} ${ENV} -f ${MONITORING_FILE} down

# --- Django ---

migrate:
	${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} migrate

migrations:
	${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} makemigrations

superuser:
	${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} createsuperuser --no-input

collectstatic:
	${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} collectstatic

dumpdata:
	${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} dumpdata ${APP_NAME} --indent=4 -o ${FILE}

loaddata:
	${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} loaddata --app=${APP_NAME} --format=json

runscheduler:
	${EXEC_IT} ${APP_CONTAINER} ${MANAGE_PY} runscheduler

# --- Tests ---

test-app:
	${DC} ${ENV} -f ${TEST_FILE} up --build -d

test-down:
	${DC} ${ENV} -f ${TEST_FILE} down

test-restart:
	${DC} ${ENV} -f ${TEST_FILE} down
	${DC} ${ENV} -f ${TEST_FILE} up -d

test-migrate:
	${EXEC} ${APP_CONTAINER} ${MANAGE_PY} migrate

test-run:
	${EXEC} ${APP_CONTAINER} pytest -v
