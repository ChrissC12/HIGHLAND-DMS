# dms_project/settings.py

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from a .env file for local development
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Use environment variables for secrets. A default is provided for local dev.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-local-key')

# DEBUG should be False in production! We read it from an environment variable.
# The 'RENDER' env var is automatically set by the Render platform.
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = []
# Render provides a hostname, which we'll add here later.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # For WhiteNoise
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'generator',
    'imagekit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # WhiteNoise Middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dms_project.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': { 'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'dms_project.wsgi.application'

# Database configuration
DATABASES = {
    'default': dj_database_url.config(
        # Use the local sqlite database if DATABASE_URL is not set
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# ... (AUTH_PASSWORD_VALIDATORS, etc. remain the same) ...
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
# For production on Render, we use a persistent disk location
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_files')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'