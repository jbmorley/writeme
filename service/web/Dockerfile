FROM python:3.10.7-slim-buster
ARG VERSION

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /tmp
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src /usr/src/app

WORKDIR /usr/src/app

RUN echo "$VERSION" > VERSION

ENTRYPOINT gunicorn --bind 0.0.0.0:9449 --pythonpath . app:app
