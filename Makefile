DC = docker compose

# Docker-compose file paths
STORAGES_FILE = docker_compose/storages.yaml
APP_FILE = docker_compose/app.yaml
APP_PROD_FILE = docker_compose/app.prod.yaml
TEST_FILE = docker_compose/test.yaml

# Docker-compose container names
APP_CONTAINER = main-app
PROXY_CONTAINER = proxy
SCHEDULER_CONTAINER = scheduler
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
.PHONY: dev dev-down dev-logs
.PHONY: prod prod-logs prod-down
.PHONY: storages storages-down storages-logs
.PHONY: proxy-logs proxy-reload tls-init-dummy tls-issue tls-renew
.PHONY: db-logs postgres cache-flush db-backup db-restore scheduler-logs
.PHONY: migrations migrate superuser loaddata dumpdata collectstatic runscheduler
.PHONY: test-app test-down test-restart test-run test-migrate test-cov

# --- App ---

dev:
	${DC} ${ENV} --profile dev -f ${APP_FILE} -f ${STORAGES_FILE} up --build -d

dev-logs:
	${LOGS} ${APP_CONTAINER} -f

dev-down:
	${DC} ${ENV} --profile dev -f ${APP_FILE} -f ${STORAGES_FILE} down

# --- App (prod) ---

prod:
	${DC} ${ENV} -f ${APP_PROD_FILE} -f ${STORAGES_FILE} up --build -d

prod-logs:
	${LOGS} ${APP_PROD_FILE} -f

prod-down:
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

# --- Backups ---
# Manual one-shot dump. Lands in BACKUP_DIR (host ./backups by default).
db-backup:
	${EXEC} ${SCHEDULER_CONTAINER} sh -c 'PGPASSWORD=$$POSTGRES_DB_PASSWORD \
		pg_dump -Fc -h $$POSTGRES_HOST -U $$POSTGRES_DB_USER -d $$POSTGRES_DB_NAME \
		-f /backups/chmnu-manual-$$(date +%Y%m%d-%H%M%S).dump'

# Restore from a dump file. Usage: make db-restore FILE=chmnu-20260606-020000.dump
# Tip: bring main-app down first so no app connections hold tables.
db-restore:
	${EXEC} ${SCHEDULER_CONTAINER} sh -c 'PGPASSWORD=$$POSTGRES_DB_PASSWORD \
		pg_restore --clean --if-exists -h $$POSTGRES_HOST -U $$POSTGRES_DB_USER \
		-d $$POSTGRES_DB_NAME /backups/${FILE}'

scheduler-logs:
	${LOGS} ${SCHEDULER_CONTAINER} -f

# --- Proxy ---

proxy-logs:
	${LOGS} ${PROXY_CONTAINER} -f

proxy-reload:
	${EXEC_IT} ${PROXY_CONTAINER} nginx -s reload

# --- TLS / certbot ---
# One-time bootstrap before first `make prod`. Seeds a self-signed cert so nginx can start;
# certbot then replaces it with a real Let's Encrypt cert via `tls-issue`.
tls-init-dummy:
	set -a; . ./.env; set +a; \
	${DC} ${ENV} -f ${APP_PROD_FILE} -f ${STORAGES_FILE} run --rm --entrypoint "sh -c \
		'mkdir -p /etc/letsencrypt/live/$${DOMAIN} && \
		openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
		-keyout /etc/letsencrypt/live/$${DOMAIN}/privkey.pem \
		-out /etc/letsencrypt/live/$${DOMAIN}/fullchain.pem \
		-subj /CN=localhost'" certbot

tls-issue:
	set -a; . ./.env; set +a; \
	${DC} ${ENV} -f ${APP_PROD_FILE} -f ${STORAGES_FILE} run --rm --entrypoint "sh -c \
		'rm -rf /etc/letsencrypt/live/$${DOMAIN} \
			/etc/letsencrypt/archive/$${DOMAIN} \
			/etc/letsencrypt/renewal/$${DOMAIN}.conf; \
		certbot certonly --webroot --webroot-path=/var/www/certbot \
		--email $${CERTBOT_EMAIL} --agree-tos --no-eff-email \
		--force-renewal -d $${DOMAIN}'" certbot
	${EXEC_IT} ${PROXY_CONTAINER} nginx -s reload

tls-renew:
	set -a; . ./.env; set +a; \
	${DC} ${ENV} -f ${APP_PROD_FILE} -f ${STORAGES_FILE} run --rm certbot renew
	${EXEC_IT} ${PROXY_CONTAINER} nginx -s reload

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

test-cov:
	${EXEC} ${APP_CONTAINER} pytest --cov=core --cov-report=term-missing
