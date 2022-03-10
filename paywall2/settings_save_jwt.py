import os
import datetime
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = '#-4)vm=f8fm#adsgno$d%2^df31zd@_eisul(x!yk^ygbidvf*'

STRIPE_PUBLIC_KEY = 'pk_test_G0m3C0rAdy14HUMjGDn0Iqcq'

STRIPE_PRIVATE_KEY = 'sk_test_poROAg38HvyUanQVlXvyVBMT'

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #REST APIs
    'rest_framework',
    'rest_framework_jwt',
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
    'nullservice',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny', 'common.permissions.ApiKeyPermission'),
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    # 'ALLOWED_VERSIONS':('2.0',)
}

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

CORS_ORIGIN_WHITELIST = (
    'localhost:9000',
    '127.0.0.1:9001',
    # 'http://127.0.0.1:9001'
)

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'DELETE',
)

CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'accept-encoding',
    'origin',
    'authorization',
    'x-csrftoken'
)

ROOT_URLCONF = 'paywall2.urls'

WSGI_APPLICATION = 'paywall2.wsgi.application'
# test
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'phoenix_api',
        'USER': 'phoenix',
        # UAT datbase credentials
        'PASSWORD': 'xrXbTZfrHdwmS7VC',
        'HOST': 'phoenix-api-uat.cwyjt5kql77y.us-west-2.rds.amazonaws.com',
        # TEST database credentials
        # 'PASSWORD': '3UPuH9zbgkrPEsbE',
        # 'HOST': 'phoenix-api-test.cwyjt5kql77y.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
    }
}

#local
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'phoenix_api_copy_20190815',
#         'USER': 'root',
#         'PASSWORD': '123',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }

#uat
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'phoenix_api',
#         'USER': 'phoenix',
#         'PASSWORD': 'xrXbTZfrHdwmS7VC',
#         'HOST': 'phoenix-api-uat.cwyjt5kql77y.us-west-2.rds.amazonaws.com',
#         'PORT': '3306',
#         'CONN_MAX_AGE': None,
#         #'OPTIONS': {
#         #   "init_command": "SET GLOBAL max_connections = 1000",
#         #}
#     }
# }

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

STATIC_URL = '/static/'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/django_mail'
EMAIL_USE_TLS = True
EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
EMAIL_PORT = 25
# Fill in the username and password for emails.
# For AWS SES, this will be the username/password of the IAM created for SES.
EMAIL_HOST_USER = 'AKIAJRTMBPEW3PKUO2IQ'
EMAIL_HOST_PASSWORD = 'Av8ltV1qECyvuoMgltOVfdS8WhQT8fs3bSez1m0OGpfb'

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=86400),
}