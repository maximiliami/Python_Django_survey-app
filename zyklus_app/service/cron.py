# cronjobs
from service.services import Service


def my_scheduled_job():
    Service.db_checkup()


def my_scheduled_job_1():
    Service.notify_via_webpush()
