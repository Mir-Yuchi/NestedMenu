# Dockerfile

# 1. Use the official Python base image matching our runtime
FROM python:3.13.5-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set workdir
WORKDIR /app

# 4. Install system dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# 5. Copy only requirements to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# 6. Install Poetry & dependencies
RUN pip install --no-cache-dir poetry \
  && poetry config virtualenvs.create false \
  && poetry install --without dev --no-root --no-interaction --no-ansi

# 7. Copy project code
COPY . /app/

# 8. Collect static (optional if you have static files)
RUN python manage.py collectstatic --no-input

# 9. Expose port & define default command
EXPOSE 8000
CMD ["gunicorn", "nestedmenu.wsgi:application", "--bind", "0.0.0.0:8000"]
