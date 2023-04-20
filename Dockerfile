FROM node:18.12-alpine as develop-stage
WORKDIR /app
COPY package*.json ./
RUN yarn global add vite
COPY . .

FROM develop-stage as build-stage
RUN yarn
RUN yarn build

FROM python:3.10-slim as production-stage

EXPOSE 5000

RUN apt-get update && \
  apt-get install -y build-essential libpq-dev && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -q -r requirements.txt

COPY . /app
COPY --from=build-stage /app/vue/dist /app/vue/dist
