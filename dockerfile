# Dockerfile

# Start with a lightweight version of Python 3.12 (slim reduces file size)
FROM python:3.12-slim

# Prevents Python from writing .pyc files (faster startup, cleaner disk)
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures logs are printed immediately to the console (helps with debugging)
ENV PYTHONUNBUFFERED=1

# Create a folder inside the container named /code and move into it
WORKDIR /code

# Copy the list of required libraries from your computer to the container
COPY requirements.txt /code/

# Install the libraries listed in the text file
# --no-cache-dir keeps the image small by not saving temporary installation files
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your project files from your computer into the container
COPY . /code/