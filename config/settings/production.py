"""
Production Django settings for the Ethical Ad Server project.

This is meant to be customized by setting environment variables.

Only a few environment variables are required:

- SECRET_KEY
- ALLOWED_HOSTS
- REDIS_URL
- DATABASE_URL
- SENDGRID_API_KEY
"""
from .base import *  # noqa
from .base import env


# Django Settings
# https://docs.djangoproject.com/en/1.11/ref/settings/
# --------------------------------------------------------------------------
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# ALLOWED_HOSTS is required in production
# eg. "adserver.yourserver.com,adserver.yourserver.io"
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
SECRET_KEY = env("SECRET_KEY")  # Django won't start unless the SECRET_KEY is non-empty
INTERNAL_IPS = env.list("INTERNAL_IPS", default=[])


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
# --------------------------------------------------------------------------
DATABASES = {
    "default": env.db()  # Raises ImproperlyConfigured exception if DATABASE_URL not set
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=3600)


# Cache
# https://docs.djangoproject.com/en/1.11/topics/cache/
# https://niwinz.github.io/django-redis/
# --------------------------------------------------------------------------
CACHES = {"default": env.cache("REDIS_URL")}

# Secure connection workaround
# https://github.com/joke2k/django-environ/pull/211
if env.bool("REDIS_SSL", default=False):
    CACHES["default"]["LOCATION"] = CACHES["default"]["LOCATION"].replace(
        "redis://", "rediss://"
    )


# Security
# https://docs.djangoproject.com/en/1.11/topics/security/
# https://docs.djangoproject.com/en/1.11/ref/middleware/#django.middleware.security.SecurityMiddleware
# https://docs.djangoproject.com/en/1.11/ref/clickjacking/
# --------------------------------------------------------------------------
if env.bool("ADSERVER_HTTPS", default=False):
    ADSERVER_HTTPS = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365  # 1 year is recommended: 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Redirect HTTP -> HTTPS
    # https://devcenter.heroku.com/articles/http-routing#heroku-headers
    # Optionally enforce a specific host. Other hosts will redirect
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    ENFORCE_HOST = env("ENFORCE_HOST", default=None)


# Email settings
# See: https://anymail.readthedocs.io
# --------------------------------------------------------------------------
INSTALLED_APPS += ["anymail"]
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
ANYMAIL = {"SENDGRID_API_KEY": env("SENDGRID_API_KEY")}


# User upload storage
# https://docs.djangoproject.com/en/1.11/topics/files/
# https://django-storages.readthedocs.io/en/latest/backends/azure.html
DEFAULT_FILE_STORAGE = env(
    "DEFAULT_FILE_STORAGE", default="storages.backends.azure_storage.AzureStorage"
)
MEDIA_URL = env("MEDIA_URL", default="")
MEDIA_ROOT = env("MEDIA_ROOT", default="")
AZURE_ACCOUNT_NAME = env("AZURE_ACCOUNT_NAME", default="")
AZURE_ACCOUNT_KEY = env("AZURE_ACCOUNT_KEY", default="")
AZURE_CONTAINER = env("AZURE_CONTAINER", default="")


# Celery settings for asynchronous tasks
# http://docs.celeryproject.org
# --------------------------------------------------------------------------
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=env("REDIS_URL"))
CELERY_RESULT_BACKEND = CELERY_BROKER_URL


# Sentry settings for error monitoring
# https://docs.sentry.io/platforms/python/django/
# --------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN", default=None)
if SENTRY_DSN:
    # pylint: disable=import-error
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()])


# Production ad server specific settings
# https://read-the-docs-ethical-ad-server.readthedocs-hosted.com/en/latest/install/configuration.html
# --------------------------------------------------------------------------
ADSERVER_ADMIN_URL = env("ADSERVER_ADMIN_URL", default="admin")
ADSERVER_ANALYTICS_ID = env("ADSERVER_ANALYTICS_ID", default=None)
ADSERVER_DO_NOT_TRACK = env.bool("ADSERVER_DO_NOT_TRACK", default=False)
ADSERVER_PRIVACY_POLICY_URL = env("ADSERVER_PRIVACY_POLICY_URL", default=None)
ADSERVER_RECORD_VIEWS = env.bool("ADSERVER_RECORD_VIEWS", default=False)
ADSERVER_BLACKLISTED_USER_AGENTS = env.list(
    "ADSERVER_BLACKLISTED_USER_AGENTS", default=[]
)
ADSERVER_CLICK_RATELIMITS = env.list(
    "ADSERVER_CLICK_RATELIMITS", default=["1/m", "3/10m", "10/h", "25/d"]
)

# GeoIP settings
# This directory should be the path to GeoLite2-City.mmdb and GeoLite2-Country.mmdb
GEOIP_PATH = env("GEOIP_GEOLITE2_PATH", default=GEOIP_PATH)
GEOIP_CITY = env("GEOIP_GEOLITE2_CITY_FILENAME", default="GeoLite2-City.mmdb")
GEOIP_COUNTRY = env("GEOIP_GEOLITE2_COUNTRY_FILENAME", default="GeoLite2-Country.mmdb")
