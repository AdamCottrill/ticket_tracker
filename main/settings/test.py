# usage: python manage.py test pjtk2 --settings=main.test_settings
# flake8: noqa

"""Settings to be used for running tests."""
import logging
import os

from main.settings.base import *

USE_TZ = False

SECRET_KEY = get_env_variable("SECRET_KEY")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)


logging.getLogger("factory").setLevel(logging.WARN)
