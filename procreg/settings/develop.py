"""
Django settings for procreg project.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .utils import discover

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = discover("django_key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ENABLE_DEBUG_TOOLBAR = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]
INTERNAL_IPS = [
    '127.0.0.1',
]

CSRF_TRUSTED_ORIGINS = [
    # None currently added in dev.py
]

# Only trust the following origins if DEBUG = True!!!
if DEBUG is True:
    CSRF_TRUSTED_ORIGINS += [
        'http://127.0.0.1:9000',
        'http://localhost:9000',
    ]

# Application definition

INSTALLED_APPS = [

    # Django model translation must come before admin
    'modeltranslation',

    # CDH Core libraries
    'cdh.core',
    'cdh.questions',
    "cdh.files",
    # 'uil.rest', # Rest client
    # 'uil.vue',  # Vue support
    
    # Django supplied apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django extensions
    'django_extensions',

    # django-simple-menu
    'simple_menu',

    # DRF - Enable if using uil.rest and/or uil.vue.FancyList
    # 'rest_framework',

    # Impersonate
    'impersonate',

    # Local apps
    'main',
    'registrations',
    "procreg",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
]

if DEBUG and ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

ROOT_URLCONF = 'procreg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "NAME": "app_dirs",
#        "APP_DIRS": True,
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "registrations/questions/templates",
            BASE_DIR / "registrations/views",
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                (
                    'django.template.loaders.app_directories.Loader'
                ),
                (
                    'django.template.loaders.filesystem.Loader',
                    [BASE_DIR / "registrations" / "views"],
                ),
            ]
        },
    },
    # {
    #     'BACKEND': 'django.template.backends.django.DjangoTemplates',
    #     "NAME": "views_subdir",
    #     'OPTIONS': {
    #         'context_processors': [
    #             'django.template.context_processors.debug',
    #             'django.template.context_processors.request',
    #             'django.contrib.auth.context_processors.auth',
    #             'django.contrib.messages.context_processors.messages',
    #         ],
    #         'loaders': [
    #             (
    #                 'django.template.loaders.filesystem.Loader',
    #                 [BASE_DIR / "registrations/views"],
    #             ),
    #         ]
    #     },
    # },
]

WSGI_APPLICATION = 'procreg.wsgi.application'

INTERNAL_IPS = [
    "127.0.0.1",
]

# LOGGING

log_file_path = "/tmp/django-procreg.log"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'logfile': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_file_path,
            'maxBytes': 50000,
            'backupCount': 3,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['logfile', 'console'],
            'propagate': True,
        },
    },
}


if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = '/tmp/django-email'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 2525
    EMAIL_FROM = 'T.D.Mees@uu.nl'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

try:
    # If we get MySQL / MariaDB credentials, attempt to connect to mysqld
    if not os.path.exists("/var/run/mysqld",):
        raise Exception("Mysqld socket not found!")
    db_name = discover("db_name")
    db_user = discover("db_user")
    db_password = discover("db_password")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            "PASSWORD": db_password,
            "USER": db_user,
            "NAME": db_name,
        }
    }
except Exception as e:
    # Otherwise, fall back to the default SQLite
    print(e)
    print("Proceeding with SQLite3...")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/persistent/db.sqlite3',
        }
    }
else:
    print("Proceeding with mysqld...")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth info

AUTH_USER_MODEL = 'main.User'

LOGIN_URL = reverse_lazy('main:login')

LOGIN_REDIRECT_URL = reverse_lazy('main:home')


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        "OPTIONS": {
            "min_length": 6,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en"
LANGUAGES = (
    ('nl', _('lang:nl')),
    ('en', _('lang:en')),
)

LOCALE_PATHS = (
    'locale',
)

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = "/var/www/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Security
# https://docs.djangoproject.com/en/2.0/topics/security/

X_FRAME_OPTIONS = 'DENY'
# Local development server doesn't support https
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 60 * 12  # 12 hours

# Django CSP
# http://django-csp.readthedocs.io/en/latest/index.html
CSP_REPORT_ONLY = False
CSP_UPGRADE_INSECURE_REQUESTS = not DEBUG
CSP_INCLUDE_NONCE_IN = ['script-src']

CSP_DEFAULT_SRC = ["'self'", ]
CSP_SCRIPT_SRC = ["'self'", ]
CSP_FONT_SRC = ["'self'", 'data:', ]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_IMG_SRC = ["'self'", 'data:', "*"]  # Remove the last one if you
# want to be really secure

# Django Simple Menu
# https://django-simple-menu.readthedocs.io/en/latest/index.html

MENU_SELECT_PARENTS = True
MENU_HIDE_EMPTY = False

# Default media directory (served statically!)
MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'


try:
    from .saml_settings import *

    # Only add stuff to settings if we actually have SAML settings
    INSTALLED_APPS += SAML_APPS
    MIDDLEWARE += SAML_MIDDLEWARE

    LOGIN_URL = reverse_lazy('saml-login')
    SHOW_SAML_LOGIN = True

    # Custom proxy model for SAML attribute processing
    SAML_USER_MODEL = 'main.SamlUserProxy'

except Exception as e:
    print("SAML:", e)
    print('Proceeding without SAML settings')
