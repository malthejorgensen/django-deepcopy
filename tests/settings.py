"""
Django settings for dj project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.getenv(
#     'SECRET_KEY', 'cw=&k(yv!=(#s+h4&051ypcgv8c1r43301oa@cui6($8hc609o'
# )

ALLOWED_HOSTS = []

# ROOT_URLCONF = 'eduflow.urls'

# Internationalization: https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

#
# LOGGING = {
#     'version': 1,
#     'handlers': {'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'}},
#     'disable_existing_loggers': False,
#     'formatters': {'simple': {'format': '{levelname} {name} {message}', 'style': '{'}},
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
#         },
#         'oauthlib': {
#             'handlers': ['console'],
#             'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
#         },
#         'requests-oauthlib': {
#             'handlers': ['console'],
#             'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
#         },
#         'eduflow': {
#             'handlers': ['console'],
#             'level': os.getenv('EDUFLOW_LOG_LEVEL', 'INFO'),
#         },
#         'auth': {
#             'handlers': ['console'],
#             'level': os.getenv('EDUFLOW_LOG_LEVEL', 'INFO'),
#         },
#         'graphql': {
#             'handlers': ['console'],
#             'level': os.getenv('EDUFLOW_LOG_LEVEL', 'INFO'),
#         },
#     },
# }

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "KEY_PREFIX": "django_cache",
#         "LOCATION": REDISCLOUD_URL,
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             # Python 3.8 upgrades to pickle protocol version 5, so if you're
#             # on version 3.8 locally, this ensures compatibility with production
#             # when running e.g. `python manage.py refresh_completion_state`
#             "PICKLE_VERSION": 4,
#         },
#     }
# }


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #
    'tests.testapp',
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

WSGI_APPLICATION = 'cartoonwiki.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Pass


# django.contrib.staticfiles
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(DJANGO_PROJECT_DIR, 'static')


# django.contrib.sites
SITE_ID = os.getenv('DJANGO_SITE_ID', None)

# django.contrib.sitemaps (our variable to override protocol)
SITEMAPS_PROTOCOL = os.getenv('SITEMAPS_PROTOCOL', 'https')
SITEMAPS_CACHE_TIMEOUT = int(os.getenv('SITEMAPS_CACHE_TIMEOUT', 0))


# django.contrib.auth
# AUTH_USER_MODEL = 'user.User'
# LOGIN_URL = '/login'
# LOGIN_REDIRECT_URL = '/'
# LOGOUT_REDIRECT_URL = '/'

# Django apps
# DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'  # Introduced django 3.2

# AUTHENTICATION_BACKENDS = [
#     'auth.core.backends.UsernameOrEmailBackend',
# ]
