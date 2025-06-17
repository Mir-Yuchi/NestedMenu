FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      postgresql-client \
      netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip \
 && pip install "poetry==1.8.1"

COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

COPY . /app/

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "nestedmenu.wsgi:application", "--bind", "0.0.0.0:8000"]
