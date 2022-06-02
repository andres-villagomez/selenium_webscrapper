# syntax=docker/dockerfile:1
FROM python:3.9.1

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy files
WORKDIR /app
COPY ./app.py /app/app.py
COPY ./requirements.txt /app/requirements.txt

RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0 app:app