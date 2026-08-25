FROM python:3.12-slim-trixie
ARG VERSION

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /tmp
COPY requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

COPY ./src /usr/src/app

WORKDIR /usr/src/app

RUN echo "$VERSION" > VERSION

ENTRYPOINT gunicorn --bind 0.0.0.0:9449 --pythonpath . app:app
