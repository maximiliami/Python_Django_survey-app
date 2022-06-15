"""
Django settings for zyklus_app project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from django.conf.global_settings import CSRF_COOKIE_DOMAIN

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Secret key for Docker
# SECRET_KEY = os.environ['DJANGO_SECRET']
SECRET_KEY = 'django-insecure-d0^)g)s47#m_f55+$)4mbzei#@jvf4ghktd+n*zkc&f+s7(sq0'

# SECURITY WARNING: don't run with debug turned on in production!
# Security for Docker
DEBUG = (bool(int(os.environ.get('DJANGO_DEBUG', 1))))

ALLOWED_HOSTS = []

# CSRF Deploy
CSRF_TRUSTED_ORIGINS = []

if 'DJANGO_CSRF_COOKIE_DOMAIN' in os.environ:
    CSRF_TRUSTED_ORIGINS.append('https://*' + os.environ['DJANGO_CSRF_COOKIE_DOMAIN'])

if 'DJANGO_CSRF_COOKIE_DOMAIN' in os.environ:
    CSRF_COOKIE_DOMAIN = (os.environ['DJANGO_CSRF_COOKIE_DOMAIN'])

# ALLOWED_HOSTS must not be empty if DEBUG == False,
# we set it with an environment-variable
if 'DJANGO_HOST' in os.environ:
    ALLOWED_HOSTS.append(os.environ['DJANGO_HOST'])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'questionnaire',
    'member',
    'django_bootstrap5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zyklus_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'zyklus_app.wsgi.application'

# Database Docker
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.environ['DB_ENGINE'],
        'NAME': os.environ['MYSQL_DATABASE'],
        'USER': os.environ['MYSQL_USERNAME'],
        'PASSWORD': os.environ['MYSQL_USERPASS'],
        'HOST': os.environ['MYSQL_SERVER'],
        'PORT': os.environ['MYSQL_PORT'],
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'de-DE'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'questionnaire.PseudoUser'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

LOGOUT_REDIRECT_URL = "member:login"
