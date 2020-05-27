FROM python:3.8-slim

RUN apt-get update && \
  apt-get install -y build-essential default-libmysqlclient-dev && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -q -r requirements.txt

COPY . /app

EXPOSE 5000
