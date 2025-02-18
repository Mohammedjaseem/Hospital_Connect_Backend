"""
Django settings for Hospital_Connect project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
from __future__ import absolute_import, unicode_literals
from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

SHARED_APPS = [
    'django_tenants',
    'app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework_simplejwt',
    'django_celery_results',
    'corsheaders',
    'custom_users',
]

TENANT_APPS = [ 
    'administration',
    'staff',
    'hostel',
    'gate_pass',
    'connect_bills',
    ]

INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django_tenants.middleware.main.TenantMainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#cors settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True



ROOT_URLCONF = 'Hospital_Connect.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'Hospital_Connect.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': '5432',
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# STATIC_URL = 'static/'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'  # URL prefix for static files
STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # Directory for collectstatic files

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




# Django Tenants Configuration
TENANT_MODEL = 'app.Client'
TENANT_DOMAIN_MODEL = 'app.Domain'
PUBLIC_SCHEMA_URLCONF = 'app.urls'



# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',  # Unauthenticated users
        'rest_framework.throttling.UserRateThrottle',  # Authenticated users
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/minute',   # 5 login attempts per minute for unauthenticated users
        'user': '10/minute',  # 10 login attempts per minute for authenticated users
    }
}


# JWT Configuration

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    # "AUTH_HEADER_TYPES": ("Bearer",),
    # "AUTH_COOKIE": "access_token",
    # "AUTH_COOKIE_HTTPONLY": True,  # Prevents JavaScript access
    # "AUTH_COOKIE_SECURE": False,  # ✅ Set to False for local development
    # "AUTH_COOKIE_SAMESITE": "None",  # ✅ Prevent cross-site issues
}


AUTHENTICATION_BACKENDS = [
    'custom_users.authentication.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'custom_users.CustomUser'



CELERY_BROKER_URL ='redis://localhost:6389/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIME_ZONE = 'Asia/Kolkata'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_RESULT_BACKEND = 'django-db'


#SMTP EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS',default=True)
EMAIL_PORT = os.getenv('EMAIL_PORT',default=587)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')



# # Settinngs for the HttpOnly Jwt Cookie

# CSRF_COOKIE_HTTPONLY = False # ✅ Allow CSRF cookie to be accessed by JavaScript
# CSRF_COOKIE_SECURE = False  # ✅ Ensure CSRF cookie works in local development
# CSRF_USE_SESSIONS = False
# CSRF_COOKIE_SAMESITE = "None"  # ✅ Match AUTH_COOKIE_SAMESITE
# CSRF_TRUSTED_ORIGINS = ["http://localhost:5173"]  # ✅ Trusted frontend origin



CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # ✅ Frontend running locally
    "https://am-connect.vercel.app",
]



CSRF_TRUSTED_ORIGINS = ["http://localhost:5173","https://am-connect.vercel.app" ]  # ✅ Trusted frontend origin


# SESSION_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SECURE = False  # ✅ Match AUTH_COOKIE_SECURE
# SESSION_COOKIE_SAMESITE = "None"  # ✅ Match CSRF and AUTH_COOKIE_SAMESITE

# # Ensure authentication cookies are also secure
# AUTH_COOKIE_HTTPONLY = True
# AUTH_COOKIE_SECURE = False
# AUTH_COOKIE_SAMESITE = 'None'



# # SECURE_SSL_REDIRECT = True  # Redirect HTTP requests to HTTPS
# SECURE_HSTS_SECONDS = 31536000  # Enforce HTTPS for one year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Needed if behind a proxy
# SECURE_BROWSER_XSS_FILTER = True  # Enable XSS protection






# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = "ap-south-1"
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"

# Static and Media Files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'  # Keep static files local
DEFAULT_FILE_STORAGE = 'utils.multis3.TenantMediaStorage'

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"







import logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "debug.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "storages": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "boto3": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "botocore": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins (Only for testing)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["Authorization", "Content-Type"]
