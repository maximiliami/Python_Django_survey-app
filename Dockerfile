FROM python:3.10

WORKDIR /zyklus_app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY ./zyklus_app/ .

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
