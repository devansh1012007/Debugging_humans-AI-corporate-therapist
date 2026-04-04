
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

# Import all required functions
from app_1.tasks import (
    my_daily_function, 
    get_report, 
    process_email_queue_task,
    cleanup_email_queue_task
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Runs APScheduler with unified task management."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # 1. Midnight Snapshot Processing (Daily)
        scheduler.add_job(
            my_daily_function,
            trigger=CronTrigger(hour=5, minute=15),
            id="my_daily_task",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added daily job: my_daily_task at 05:15.")

        # 2. Corporate Report Generation (Every 15 Days)
        scheduler.add_job(
            get_report,
            trigger=IntervalTrigger(days=15),  
            id="my_15_day_task",               
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added 15-day interval job: my_15_day_task.")

        # 3. Email Queue Processor (Hourly)
        # Executes every hour to ensure emails dispatch reliably once reports are generated.
        scheduler.add_job(
            process_email_queue_task,
            trigger=IntervalTrigger(hours=1),
            id="process_email_queue_task",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added hourly job: process_email_queue_task.")

        # 4. Database Cleanup (Weekly)
        # Removes old log data from the database to maintain performance.
        scheduler.add_job(
            cleanup_email_queue_task,
            trigger=IntervalTrigger(days=7),
            id="cleanup_email_queue_task",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: cleanup_email_queue_task.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")