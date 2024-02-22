FROM python:3.10

COPY .env .

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade pip &&\
    pip install --no-cache-dir -r requirements.txt

COPY .  .

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]