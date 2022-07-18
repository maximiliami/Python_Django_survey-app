FROM python:3.10

RUN apt-get update
RUN apt-get install -y cron
RUN apt-get install -y vim

WORKDIR /zyklus-app_1
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY ./zyklus_app/ .

EXPOSE 8000
ENTRYPOINT ["./docker_entrypoint.sh"]
CMD ["./db_migration.sh"]
