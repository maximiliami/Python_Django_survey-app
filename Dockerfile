FROM python:3.10

WORKDIR /zyklus-app_1
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY ./zyklus_app/ .

EXPOSE 8000
CMD ["./db_migration.sh"]
