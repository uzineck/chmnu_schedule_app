from django.conf import settings
from django.core.management.base import BaseCommand

import logging
import os
import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import (
    datetime,
    timedelta,
)
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from pathlib import Path

from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.project.containers.containers import get_container


logger = logging.getLogger(__name__)


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def backup_database():
    backup_dir = Path(os.environ.get("BACKUP_DIR", "/backups"))
    retention_days = int(os.environ.get("BACKUP_RETENTION_DAYS", "30"))
    backup_dir.mkdir(parents=True, exist_ok=True)

    db = settings.DATABASES["default"]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = backup_dir / f"chmnu-{timestamp}.dump"

    env = {**os.environ, "PGPASSWORD": db["PASSWORD"]}
    cmd = [
        "pg_dump",
        "-Fc",
        "-h", db["HOST"],
        "-U", db["USER"],
        "-d", db["NAME"],
        "-f", str(target),
    ]

    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("pg_dump failed (rc=%s): %s", result.returncode, result.stderr.strip())
        if target.exists():
            target.unlink()
        return

    logger.info("Database backed up to %s (%s bytes)", target, target.stat().st_size)

    cutoff = datetime.now() - timedelta(days=retention_days)
    for old in backup_dir.glob("chmnu-*.dump"):
        if datetime.fromtimestamp(old.stat().st_mtime) < cutoff:
            old.unlink()
            logger.info("Pruned old backup %s", old.name)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        container = get_container()
        issued_jwt_token_service: BaseIssuedJwtTokenService = container.resolve(BaseIssuedJwtTokenService)
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            issued_jwt_token_service.delete_expired_tokens,
            trigger=CronTrigger(hour="01", minute="00"),
            id="delete_expired_jwt_tokens",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added daily job: 'delete_expired_jwt_tokens'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00",
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'.",
        )

        scheduler.add_job(
            backup_database,
            trigger=CronTrigger(hour="02", minute="00"),
            id="backup_database",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added daily job: 'backup_database'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
