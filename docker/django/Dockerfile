FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN apt-get update && apt-get install -y build-essential libpq-dev gcc git curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code/

# Ensure appuser can write to /code and shared runtime volumes.
RUN adduser --disabled-password --gecos "" appuser || true
RUN chown -R appuser:appuser /code /tmp

USER appuser

# Ensure entrypoint is executable if present

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
