FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install system dependencies (needed for some Python packages like psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
# Make sure gunicorn is in your requirements.txt!

COPY . /code/


CMD ["gunicorn", "backend_AI_Corporate_therapist.wsgi:application", "--bind", "0.0.0.0:8000"]