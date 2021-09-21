FROM python:3.9-slim

EXPOSE 5000

RUN apt-get update && \
  apt-get install -y build-essential libpq-dev && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -q -r requirements.txt

COPY . /app
