import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

# Import the function you want to run
from app_1.tasks import my_daily_function 

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Schedule the function
        scheduler.add_job(
            my_daily_function,
            trigger=CronTrigger(hour=0, minute=0),  # Runs at Midnight daily
            id="my_daily_task",  # The `id` should be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added daily job: my_daily_task.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")