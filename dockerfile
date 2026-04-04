FROM python:3.12-slim

# Prevent Python from writing pyc files and keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install system dependencies required for PostgreSQL compilation
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /code/

# Ensure the entrypoint script is executable
COPY entrypoint.sh /code/
RUN sed -i 's/\r$//' /code/entrypoint.sh && chmod +x /code/entrypoint.sh

RUN adduser --disabled-password --gecos '' django-user
RUN chown -R django-user:django-user /code

# Switch to the non-root user
USER django-user

# Expose the port Render expects
EXPOSE 10000

# Set the entrypoint script to govern container startup
CMD ["/code/entrypoint.sh"]