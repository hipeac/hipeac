FROM python:3.7-alpine

# ensure Alpine Linux includes the necessary packages
RUN apk add --no-cache bash \
        libxml2 libxslt \
        mariadb-connector-c mysql-client \
    && apk add --virtual .build build-base \
        libxml2-dev libxslt-dev \
        mariadb-connector-c-dev

# install app
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -q -r requirements.txt \
    && apk del .build
COPY . /app

ENV NLTK_DATA=/app/nltk_data

EXPOSE 5000
