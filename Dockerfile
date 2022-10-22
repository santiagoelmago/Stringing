# syntax=docker/dockerfile:1
FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

ENV PORT 5000

# Expose passed env var port.
EXPOSE 5000

# Using gunicorn to handle multiple users at the same time.
CMD [ "gunicorn", "-w", "2", "main:app"]
