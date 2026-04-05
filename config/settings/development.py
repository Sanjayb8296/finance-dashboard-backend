from .base import *  # noqa: F401, F403

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "finance_db",
        "USER": "postgres",
        "PASSWORD": "Sanjayb8296@",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Disable throttling in development
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
