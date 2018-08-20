FROM python:3.7

# install wkhtmltopdf
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz && \
    tar -xvJ -f wkhtmltox-0.12.4_linux-generic-amd64.tar.xz wkhtmltox/bin/wkhtmltopdf && \
    mv wkhtmltox/bin/wkhtmltopdf /usr/bin && \
    rm -rf wkhtmltox && \
    rm wkhtmltox-0.12.4_linux-generic-amd64.tar.xz

# install app
RUN mkdir /app
WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv && pipenv install --deploy --system
COPY . /app

ENV DJANGO_ENV=production
ENV NLTK_DATA=/app/nltk_data

EXPOSE 5000
