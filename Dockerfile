FROM python:3.7-alpine

# install wkhtmltopdf
RUN apk add --no-cache wkhtmltopdf \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/

WORKDIR /app
COPY requirements.txt /app/

# ensure Alpine Linux includes the necessary packages
RUN apk add --no-cache bash \
        libxml2 libxslt \
        mariadb-connector-c mysql-client \
        freetype jpeg libpng libwebp lcms2 openjpeg tiff zlib \
    && apk add --virtual .build build-base \
        libxml2-dev libxslt-dev \
        mariadb-connector-c-dev \
        freetype-dev jpeg-dev libpng-dev libwebp-dev lcms2-dev openjpeg-dev tiff-dev zlib-dev \
    && pip install --no-cache-dir -q -r requirements.txt \
    && apk del .build

COPY . /app
ENV NLTK_DATA=/app/nltk_data

EXPOSE 5000
