# cronjobs
from service.services import Service


def my_scheduled_job():
    Service.db_checkup()
