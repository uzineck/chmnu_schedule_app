from django.conf import settings
from django.core.management.base import BaseCommand

import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from core.apps.clients.services.issuedjwttoken import BaseIssuedJwtTokenService
from core.project.containers.containers import get_container


logger = logging.getLogger(__name__)


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        container = get_container()
        issued_jwt_token_service: BaseIssuedJwtTokenService = container.resolve(BaseIssuedJwtTokenService)
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            issued_jwt_token_service.delete_expired_tokens,
            trigger=CronTrigger(day_of_week="sun", hour="00", minute="00"),
            id="delete_expired_jwt_tokens",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'delete_expired_jwt_tokens'.")

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

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
