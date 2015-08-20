#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.





"""
Django settings for paywall2 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#-4)vm=f8fm#adsgno$d%2^df31zd@_eisul(x!yk^ygbidvf*'

STRIPE_PUBLIC_KEY = 'pk_test_VEu0r74glZkzeT8IXLmXxojP'

STRIPE_PRIVATE_KEY = 'sk_test_dXy85QkwH66s64bIWKbikyMt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #REST APIs
    'rest_framework',
    #Other
    'corsheaders',
    #Custom Apps
    'metering',
    'subscription',
    'authorization',
    'partner',
    'party',
    'loggingapp',
    'apikey',
    'common',
    'authentication',
    'cookies',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny','common.permissions.ApiKeyPermission'),
    'PAGE_SIZE': 10
}

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

# CORS Setting to allow ui sites to access the API server
CORS_ORIGIN_WHITELIST = (
    'testui.steveatgetexp.com',
    'azeem.steveatgetexp.com',
)

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'UPDATE',
)

CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken'
)

ROOT_URLCONF = 'paywall2.urls'

WSGI_APPLICATION = 'paywall2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'paywall2Test',
        'USER': 'phoenix',
        'PASSWORD': 'phoenix123',
#        'HOST': 'paywalltestmysqldb.c871k9lscygy.us-east-1.rds.amazonaws.com',
        'HOST': 'paywall2.cwyjt5kql77y.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True

SESSION_COOKIE_SECURE = True

X_FRAME_OPTIONS = 'DENY'

CSRF_COOKIE_HTTPONLY = True

CSRF_COOKIE_SECURE = True

# These parameters enforces the entire domain to use SSL. Since testing
# is done via http, it is off for development, but need to turn ON for
# production.

#SECURE_SSL_REDIRECT = True

#SECURE_HSTS_SECONDS = 1

#SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

EMAIL_USE_TLS = True
EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
EMAIL_PORT = 25
# Fill in the username and password for emails. 
# For AWS SES, this will be the username/password of the IAM created for SES.
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
