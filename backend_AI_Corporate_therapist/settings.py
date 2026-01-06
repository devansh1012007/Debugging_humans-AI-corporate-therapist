# settings.py
from pathlib import Path
import os
from datetime import timedelta 
# Import library to read .env files (files that hold secret passwords)
from dotenv import load_dotenv

# Load the secret environment variables
load_dotenv()
env = os.getenv

# Define the base folder of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Key (Should be kept secret in production)
SECRET_KEY = env('SECRET_KEY', default='django-insecure-!&p4_a3_(x65@1c*m_93#dztsav#1lj!m0s4z0d@b$wkn8s$l7')

# Debug Mode: True means show detailed errors (Good for dev, bad for production)
DEBUG = True

# Allowed Hosts: Who can connect to this server ('*' means everyone)
ALLOWED_HOSTS = ['*']

# List of installed components
INSTALLED_APPS = [
    'django.contrib.admin', # Admin panel
    'django.contrib.auth',  # User management
    'django.contrib.contenttypes',
    'django.contrib.sessions', 
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt', # Tool for secure login tokens
    'rest_framework', # The main API toolkit
    'corsheaders', # Tool to allow frontend to talk to backend
    'app_1', # Your specific application code
]

SITE_ID = 1

# Middleware: Security guards that check every request before it reaches the view
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Handles Cross-Origin Resource Sharing
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Point to the main URL configuration file
ROOT_URLCONF = 'backend_AI_Corporate_therapist.urls'

# Configuration for HTML templates (not heavily used in API only backends)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# The application object used by servers to run the code
WSGI_APPLICATION = 'backend_AI_Corporate_therapist.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql', # Using PostgreSQL database
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'mysecreatpassword'),
        'HOST': os.environ.get('DB_HOST', 'db'), # Connects to a service named 'db' (likely in Docker)
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Rules for password strength
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization settings
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'

# DRF Configuration
REST_FRAMEWORK = {
    # Enforce that users must use JWT Tokens or Sessions to access data
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# JWT Token Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30), # Login lasts 30 mins
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1), # Can refresh login for 1 day
    'ROTATE_REFRESH_TOKENS': True, 
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Redirects after login/logout
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
# Allow requests from any website (Useful for development, risky for production)
CORS_ALLOW_ALL_ORIGINS = True