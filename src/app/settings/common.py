"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import os
import warnings
from importlib import reload

import environ
import requests
import sys

from corsheaders.defaults import default_headers
from datetime import timedelta

from app.utils import secret_key_gen

env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ENV = env('ENVIRONMENT', default='local')
if ENV not in ('local', 'dev', 'staging', 'production'):
    warnings.warn('ENVIRONMENT env variable must be one of local, dev, staging or production')

if 'DJANGO_SECRET_KEY' not in os.environ:
    secret_key_gen()

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

HOSTED_SEATS_LIMIT = int(os.environ.get('HOSTED_SEATS_LIMIT', 0))

# Google Analytics Configuration
GOOGLE_ANALYTICS_KEY = os.environ.get('GOOGLE_ANALYTICS_KEY', '')
GOOGLE_SERVICE_ACCOUNT = os.environ.get('GOOGLE_SERVICE_ACCOUNT')
if not GOOGLE_SERVICE_ACCOUNT:
    warnings.warn("GOOGLE_SERVICE_ACCOUNT not configured, getting organisation usage will not work")
GA_TABLE_ID = os.environ.get('GA_TABLE_ID')
if not GA_TABLE_ID:
    warnings.warn("GA_TABLE_ID not configured, getting organisation usage will not work")

INFLUXDB_TOKEN = env.str('INFLUXDB_TOKEN', default='')
INFLUXDB_BUCKET = env.str('INFLUXDB_BUCKET', default='')
INFLUXDB_URL = env.str('INFLUXDB_URL', default='')
INFLUXDB_ORG = env.str('INFLUXDB_ORG', default='')

if 'DJANGO_ALLOWED_HOSTS' in os.environ:
    ALLOWED_HOSTS = os.environ['DJANGO_ALLOWED_HOSTS'].split(',')
else:
    ALLOWED_HOSTS = []

INTERNAL_IPS = ['127.0.0.1',]

# In order to run a load balanced solution, we need to whitelist the internal ip
try:
    internal_ip = requests.get('http://instance-data/latest/meta-data/local-ipv4').text
except requests.exceptions.ConnectionError:
    pass
else:
    ALLOWED_HOSTS.append(internal_ip)
del requests

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding("utf-8")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django.contrib.sites',
    'custom_auth',
    'api',
    'corsheaders',
    'users',
    'organisations',
    'projects',

    'environments',
    'environments.permissions',
    'environments.identities',
    'environments.identities.traits',

    'features',
    'segments',
    'e2etests',
    'simple_history',
    'debug_toolbar',
    'drf_yasg2',
    'audit',
    'permissions',
    'projects.tags',

    # 2FA
    'trench',

    # health check plugins
    'health_check',
    'health_check.db',

    # Used for ordering models (e.g. FeatureSegment)
    'ordered_model',

    'axes',
]

if GOOGLE_ANALYTICS_KEY or INFLUXDB_TOKEN:
    INSTALLED_APPS.append('analytics')

SITE_ID = 1

# Initialise empty databases dict to be populated in environment settings
DATABASES = {}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'PAGE_SIZE': 10,
    'UNICODE_JSON': False,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_THROTTLE_RATES': {
        'login': '1/s'
    }
}

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'axes.middleware.AxesMiddleware',
]

if GOOGLE_ANALYTICS_KEY:
    MIDDLEWARE.append('analytics.middleware.GoogleAnalyticsMiddleware')

if INFLUXDB_TOKEN:
    MIDDLEWARE.append('analytics.middleware.InfluxDBMiddleware')

ALLOWED_ADMIN_IP_ADDRESSES = env.list('ALLOWED_ADMIN_IP_ADDRESSES', default=list())
if len(ALLOWED_ADMIN_IP_ADDRESSES) > 0:
    warnings.warn('Restricting access to the admin site for ip addresses %s' % ', '.join(ALLOWED_ADMIN_IP_ADDRESSES))
    MIDDLEWARE.append('app.middleware.AdminWhitelistMiddleware')

ROOT_URLCONF = 'app.urls'

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

WSGI_APPLICATION = 'app.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, '../../static/')

# CORS settings

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = default_headers + (
    'X-Environment-Key',
    'X-E2E-Test-Auth-Token'
)

DEFAULT_FROM_EMAIL = "noreply@bullet-train.io"
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@bullet-train.io')
EMAIL_CONFIGURATION = {
    # Invitations with name is anticipated to take two arguments. The persons name and the
    # organisation name they are invited to.
    'INVITE_SUBJECT_WITH_NAME': '%s has invited you to join the organisation \'%s\' on Bullet '
                                'Train',
    # Invitations without a name is anticipated to take one arguments. The organisation name they
    # are invited to.
    'INVITE_SUBJECT_WITHOUT_NAME': 'You have been invited to join the organisation \'%s\' on '
                                   'Bullet Train',
    # The email address invitations will be sent from.
    'INVITE_FROM_EMAIL': SENDER_EMAIL,

}

AWS_SES_REGION_NAME = os.environ.get('AWS_SES_REGION_NAME')
AWS_SES_REGION_ENDPOINT = os.environ.get('AWS_SES_REGION_ENDPOINT')

# Used on init to create admin user for the site, update accordingly before hitting /auth/init
ALLOW_ADMIN_INITIATION_VIA_URL = True
ADMIN_EMAIL = "admin@example.com"
ADMIN_INITIAL_PASSWORD = "password"

AUTH_USER_MODEL = 'users.FFAdminUser'

ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'  # TODO: configure email verification

# SendGrid
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'sgbackend.SendGridBackend')
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
if EMAIL_BACKEND == 'sgbackend.SendGridBackend' and not SENDGRID_API_KEY:
    warnings.warn(
        "`SENDGRID_API_KEY` has not been configured. You will not receive emails.")

SWAGGER_SETTINGS = {
    'SHOW_REQUEST_HEADERS': True,
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }
}

LOGIN_URL = "/admin/login/"
LOGOUT_URL = "/admin/logout/"

# Email associated with user that is used by front end for end to end testing purposes
FE_E2E_TEST_USER_EMAIL = "nightwatch@solidstategroup.com"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Chargebee
ENABLE_CHARGEBEE = os.environ.get('ENABLE_CHARGEBEE', False)
CHARGEBEE_API_KEY = os.environ.get('CHARGEBEE_API_KEY')
CHARGEBEE_SITE = os.environ.get('CHARGEBEE_SITE')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console_format': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console_format',
        },
    },
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['console']
        },
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    }
}

CACHE_FLAGS_SECONDS = int(os.environ.get('CACHE_FLAGS_SECONDS', 0))
FLAGS_CACHE_LOCATION = 'environment-flags'
ENVIRONMENT_CACHE_LOCATION = 'environment-objects'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    },
    ENVIRONMENT_CACHE_LOCATION: {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ENVIRONMENT_CACHE_LOCATION
    },
    FLAGS_CACHE_LOCATION: {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': FLAGS_CACHE_LOCATION,
    }
}

LOG_LEVEL = env.str('LOG_LEVEL', 'WARNING')

TRENCH_AUTH = {
    'FROM_EMAIL': DEFAULT_FROM_EMAIL,
    'BACKUP_CODES_QUANTITY': 5,
    'BACKUP_CODES_LENGTH': 10,  # keep (quantity * length) under 200
    'BACKUP_CODES_CHARACTERS': (
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    ),
    'DEFAULT_VALIDITY_PERIOD': 30,
    'CONFIRM_BACKUP_CODES_REGENERATION_WITH_CODE': True,
    'APPLICATION_ISSUER_NAME': 'app.bullet-train.io',
    'MFA_METHODS': {
        'app': {
            'VERBOSE_NAME': 'TOTP App',
            'VALIDITY_PERIOD': 60 * 10,
            'USES_THIRD_PARTY_CLIENT': True,
            'HANDLER': 'custom_auth.mfa.backends.application.CustomApplicationBackend',
        },
    },
}

DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': 'password-reset/confirm/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'SERIALIZERS': {
        'token': 'custom_auth.serializers.CustomTokenSerializer',
        'user_create': 'custom_auth.serializers.CustomUserCreateSerializer',
        'current_user': 'users.serializers.CustomCurrentUserSerializer',
    },
    'SET_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
    'HIDE_USERS': True,
    'PERMISSIONS': {
        'user': ['custom_auth.permissions.CurrentUser'],
        'user_list': ['custom_auth.permissions.CurrentUser'],
    }
}


# Github OAuth credentials
GITHUB_CLIENT_ID = env.str('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = env.str('GITHUB_CLIENT_SECRET', '')

# Django Axes settings
AXES_COOLOFF_TIME = timedelta(minutes=env.int('AXES_COOLOFF_TIME', 15))
